from utils import load_config, pretty_print_json
from accesslink import AccessLink
import sqlite3
import os


class PolarToSql:

    def __init__(self, configs):
        self.accounts = []
        for db_name, in_configs in configs.items():
            for in_config in in_configs:
                account = dict()
                account["config"] = load_config(in_config)
                account["db_name"] = db_name

                if "access_token" not in account["config"]:
                    print("Authorization is required. Run authorization.py first.")
                    return

                account["accesslist_api"] = AccessLink(client_id=account["config"]["client_id"],
                                                       client_secret=account["config"]["client_secret"])

                self.db_create_if_needed(account["db_name"])
                self.accounts.append(account)

    def save_new_data(self):
        for account in self.accounts:
            available_data = account["accesslist_api"].pull_notifications.list()

            if not available_data:
                print("No new data...")
                return

            for item in available_data["available-user-data"]:
                if item["data-type"] == "EXERCISE":
                    self.save_new_exercises(account)
                elif item["data-type"] == "ACTIVITY_SUMMARY":
                    self.save_new_daily_activity_summaries(account)
                elif item["data-type"] == "PHYSICAL_INFORMATION":
                    self.save_new_physical_info(account)

    def save_new_physical_info(self, account):
        transaction = account["accesslink_api"].physical_info.create_transaction(user_id=account["config"]["user_id"],
                                                                                 access_token=account["config"]["access_token"])

        user_info = account["accesslink_api"].users.get_information(user_id=account["config"]["user_id"],
                                                                    access_token=account["config"]["access_token"])

        if not transaction:
            print("No new physical info")
            return

        resource_urls = transaction.list_physical_infos()["physical-informations"]

        db_physical_info = []

        extra_info_value = []
        extra_info_index = []
        extra_info_name = []
        for extra_info in user_info.get("extra-info"):
            extra_info_value.append(str(extra_info.get("value")))
            extra_info_index.append(str(extra_info.get("index")))
            extra_info_name.append(str(extra_info.get("name")))

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)
            #pretty_print_json(physical_info)
            db_physical_info.append([
                physical_info.get("id"),
                physical_info.get("transaction-id"),
                physical_info.get("created"),
                physical_info.get("polar-user"),
                physical_info.get("weight"),
                physical_info.get("height"),
                physical_info.get("weight-source"),
                physical_info.get("maximum-heart-rate"),
                physical_info.get("resting-heart-rate"),
                physical_info.get("aerobic-threshold"),
                physical_info.get("anaerobic-threshold"),
                physical_info.get("vo2-max"),
                user_info.get("birthdate"),
                user_info.get("gender"),
                user_info.get("first-name"),
                user_info.get("last-name"),
                user_info.get("member-id"),
                user_info.get("polar-user-id"),
                user_info.get("registration-date"),
                ";".join(extra_info_value),
                ";".join(extra_info_index),
                ";".join(extra_info_name)
            ])

        self.db_add_to_table(account["db_name"], "physical_information", db_physical_info)

        transaction.commit()

    def save_new_exercises(self, account):
        transaction = account["accesslink_api"].training_data.create_transaction(user_id=account["config"]["user_id"],
                                                                                 access_token=account["config"]["access_token"])
        if not transaction:
            print("No new exercise")
            return

        resource_urls = transaction.list_exercises()["exercises"]

        db_values_exercise = []
        db_values_heart_rate_zones = []
        db_values_samples = []

        for url in resource_urls:
            exercise_summary = transaction.get_exercise_summary(url)
            # pretty_print_json(exercise_summary)
            db_values_exercise.append([
                exercise_summary.get("calories"),
                exercise_summary.get("detailed-sport-info"),
                exercise_summary.get("device"),
                exercise_summary.get("duration"),
                exercise_summary.get("has-route"),
                exercise_summary.get("heart-rate").get("average"),
                exercise_summary.get("heart-rate").get("maximum"),
                exercise_summary.get("id"),
                exercise_summary.get("polar-user"),
                exercise_summary.get("sport"),
                exercise_summary.get("start-time"),
                exercise_summary.get("training-load"),
                exercise_summary.get("transaction-id"),
                exercise_summary.get("upload-time")
            ])

            heart_rate_zones = transaction.get_heart_rate_zones(url)
            # pretty_print_json(heart_rate_zones)
            for zone in heart_rate_zones.get("zone"):
                db_values_heart_rate_zones.append([
                    exercise_summary.get("id"),
                    zone.get("in-zone"),
                    zone.get("index"),
                    zone.get("lower-limit"),
                    zone.get("upper-limit")
                ])

            exercise_samples_types = transaction.get_available_samples(url)
            for samples_url in exercise_samples_types.get("samples"):
                exercise_samples = transaction.get_samples(samples_url)
                for data in exercise_samples["data"].split(','):
                    db_values_samples.append([
                        None,  # Auto incremented field
                        exercise_summary.get("id"),
                        exercise_samples.get("recording-rate"),
                        exercise_samples.get("sample-type"),
                        float(data)
                    ])

        self.db_add_to_table(account["db_name"], "exercise_summaries", db_values_exercise)
        self.db_add_to_table(account["db_name"], "exercise_heart_rate_zones", db_values_heart_rate_zones)
        self.db_add_to_table(account["db_name"], "exercise_samples", db_values_samples)

        transaction.commit()

    def save_new_daily_activity_summaries(self, account):
        transaction = account["accesslink_api"].daily_activity.create_transaction(user_id=account["config"]["user_id"],
                                                                                  access_token=account["config"]["access_token"])
        if not transaction:
            print("No new daily activity")
            return

        resource_urls = transaction.list_activities()["activity-log"]

        db_values_activity_summary = []
        for url in resource_urls:
            activity_summary = transaction.get_activity_summary(url)
            #pretty_print_json(activity_summary)
            db_values_activity_summary.append([
                activity_summary.get("active-calories"),
                activity_summary.get("active-steps"),
                activity_summary.get("calories"),
                activity_summary.get("created"),
                activity_summary.get("date"),
                activity_summary.get("duration"),
                activity_summary.get("id"),
                activity_summary.get("polar-user"),
                activity_summary.get("transaction-id")
            ])

        self.db_add_to_table(account["db_name"], "daily_activity_summaries", db_values_activity_summary)

        transaction.commit()

    def db_create_if_needed(self, db_name):
        if os.path.exists(db_name):
            print("Will append to existing database")
            return
        with open("create_db.sql", "r") as f:
            db_connect = sqlite3.connect(db_name)
            cur = db_connect.cursor()
            cur.executescript(f.read())
            db_connect.close()

    def db_get_table(self, db_name, table_name):
        db_connect = sqlite3.connect(db_name)
        cur = db_connect.execute('select * from %s' % table_name)
        result = cur.fetchall()
        db_connect.close()
        return result

    def db_add_to_table(self, db_name, table_name, values):
        val_placeholders = ",".join("?" * len(values[0]))
        db_connect = sqlite3.connect(db_name)
        db_connect.executemany("INSERT INTO {} VALUES ({})".format(table_name, val_placeholders), values)
        db_connect.commit()
        db_connect.close()


if __name__ == "__main__":
    database_name = "test.db"
    poltosql = PolarToSql({database_name: ["config.yml"]})
    poltosql.save_new_data()
    # prints
    print("Print physical_information table")
    print(poltosql.db_get_table(database_name, "physical_information"))
