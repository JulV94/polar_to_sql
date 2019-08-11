from utils import load_config, pretty_print_json
from accesslink import AccessLink
import sqlite3
import os


class PolarToSql:

    def __init__(self, config_filename, db_name):
        self.config = load_config(config_filename)
        self.db_name = db_name

        if "access_token" not in self.config:
            print("Authorization is required. Run authorization.py first.")
            return

        self.accesslink = AccessLink(client_id=self.config["client_id"],
                                     client_secret=self.config["client_secret"])

        self.user_info = self.accesslink.users.get_information(user_id=self.config["user_id"],
                                                               access_token=self.config["access_token"])

        self.db_create_if_needed()

    def save_new_data(self):
        available_data = self.accesslink.pull_notifications.list()

        if not available_data:
            print("No new data...")
            return

        for item in available_data["available-user-data"]:
            if item["data-type"] == "EXERCISE":
                self.save_new_exercises()
            elif item["data-type"] == "ACTIVITY_SUMMARY":
                self.save_new_daily_activity_summaries()
            elif item["data-type"] == "PHYSICAL_INFORMATION":
                self.save_new_physical_info()

    def save_new_physical_info(self):
        transaction = self.accesslink.physical_info.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])

        if not transaction:
            print("No new physical info")
            return

        resource_urls = transaction.list_physical_infos()["physical-informations"]

        db_physical_info = []

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)
            #pretty_print_json(physical_info)
            db_physical_info.append([
                physical_info.get("created"),
                physical_info.get("height"),
                physical_info.get("id"),
                physical_info.get("polar-user"),
                physical_info.get("transaction-id"),
                physical_info.get("weight"),
                physical_info.get("weight-source")
            ])

        self.db_add_to_table("physical_information", db_physical_info)

        transaction.commit()

    def save_new_exercises(self):
        transaction = self.accesslink.training_data.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
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
                        exercise_summary.get("id"),
                        exercise_samples.get("recording-rate"),
                        exercise_samples.get("sample-type"),
                        float(data)
                    ])

        self.db_add_to_table("exercise_summaries", db_values_exercise)
        self.db_add_to_table("exercise_heart_rate_zones", db_values_heart_rate_zones)
        self.db_add_to_table("exercise_samples", db_values_samples)

        transaction.commit()

    def save_new_daily_activity_summaries(self):
        transaction = self.accesslink.daily_activity.create_transaction(user_id=self.config["user_id"],
                                                                        access_token=self.config["access_token"])
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

        self.db_add_to_table("daily_activity_summaries", db_values_activity_summary)

        transaction.commit()

    def db_create_if_needed(self):
        if os.path.exists(self.db_name):
            print("Will append to existing database")
            return
        with open("create_db.sql", "r") as f:
            db_connect = sqlite3.connect(self.db_name)
            cur = db_connect.cursor()
            cur.executescript(f.read())
            db_connect.close()

    def db_get_table(self, table_name):
        db_connect = sqlite3.connect(self.db_name)
        cur = db_connect.execute('select * from %s' % table_name)
        result = cur.fetchall()
        db_connect.close()
        return result

    def db_add_to_table(self, table_name, values):
        val_placeholders = "?," * len(values[0])
        db_connect = sqlite3.connect('test.db')
        db_connect.executemany("INSERT INTO %s VALUES (%s)" % (table_name, val_placeholders[:-1]), values)
        db_connect.commit()
        db_connect.close()


if __name__ == "__main__":
    poltosql = PolarToSql("config.yml", "test.db")
    poltosql.save_new_data()
    # prints
    print("Print physical_information table")
    print(poltosql.db_get_table("physical_information"))
    print("Print daily_activity_summaries table")
    print(poltosql.db_get_table("daily_activity_summaries"))
    print("Print exercise_summaries table")
    print(poltosql.db_get_table("exercise_summaries"))
    print("Print exercise_heart_rate_zones table")
    print(poltosql.db_get_table("exercise_heart_rate_zones"))
    print("Print exercise_samples table")
    print(poltosql.db_get_table("exercise_samples"))
