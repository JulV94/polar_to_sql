from utils import load_config, save_config, pretty_print_json
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

    def get_user_information(self):
        pretty_print_json(self.user_info)

    def save_new_data(self):
        available_data = self.accesslink.pull_notifications.list()

        if not available_data:
            print("No new data...")
            return

        for item in available_data["available-user-data"]:
            if item["data-type"] == "EXERCISE":
                self.save_new_exercises()
            elif item["data-type"] == "ACTIVITY_SUMMARY":
                self.save_new_daily_activities()
            elif item["data-type"] == "PHYSICAL_INFORMATION":
                self.save_new_physical_info()

    def save_new_physical_info(self):
        transaction = self.accesslink.physical_info.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])

        if not transaction:
            return

        print("Physical info have changed, maybe watch user changed")
        resource_urls = transaction.list_physical_infos()["physical-informations"]

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)

            print("Physical info:")
            pretty_print_json(physical_info)

        transaction.commit()

    def save_new_exercises(self):
        transaction = self.accesslink.training_data.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
        if not transaction:
            return

        print("There is new exercises")

        resource_urls = transaction.list_exercises()["exercises"]

        for url in resource_urls:
            exercise_summary = transaction.get_exercise_summary(url)
            exercise_heart_rate_zones = transaction.get_heart_rate_zones(url)

            print("Exercise summary:")
            pretty_print_json(exercise_summary)
            print("Exercise heart rate zones:")
            pretty_print_json(exercise_heart_rate_zones)

        transaction.commit()

    def save_new_daily_activities(self):
        transaction = self.accesslink.daily_activity.create_transaction(user_id=self.config["user_id"],
                                                                        access_token=self.config["access_token"])
        if not transaction:
            return

        print("There is new exercises")

        resource_urls = transaction.list_activities()["activity-log"]

        for url in resource_urls:
            activity_summary = transaction.get_activity_summary(url)

            print("Activity summary:")
            pretty_print_json(activity_summary)

        transaction.commit()

    def db_create_if_needed(self):
        if os.path.exists(self.db_name):
            print("Database already created")
            return
        db_connect = sqlite3.connect(self.db_name)
        db_connect.execute("CREATE TABLE urbandictionary (SEARCH_WORD TEXT NOT NULL, SEARCH_STRING TEXT NOT NULL)")
        db_connect.close()

    def db_print(self):
        db_connect = sqlite3.connect(self.db_name)
        cur = db_connect.execute('select * from urbandictionary')
        print([dict(search_word=row[0], search_string=row[1]) for row in cur.fetchall()])
        db_connect.close()

    def db_add_test(self, a, b):
        db_connect = sqlite3.connect('test.db')
        db_connect.execute("INSERT INTO urbandictionary (SEARCH_WORD, SEARCH_STRING) \
              VALUES (?,?)", [a, b])
        db_connect.commit()
        db_connect.close()


if __name__ == "__main__":
    poltosql = PolarToSql("config.yml", "test.db")
    poltosql.get_user_information()
    poltosql.save_new_data()
    print("Transaction terminated")

    poltosql.db_create_if_needed()
    poltosql.db_print()
    poltosql.db_add_test("a", "b")
    poltosql.db_print()
    print("End of db test")
