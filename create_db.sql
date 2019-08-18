-- Physical information table
CREATE TABLE physical_information
(
    "id" INTEGER,
    "transaction-id" INTEGER,
    "created" DATETIME,
    "polar-user" VARCHAR(1023),
    "weight" FLOAT,
    "height" FLOAT,
    "weight-source" VARCHAR(255),
    "maximum-heart-rate" INTEGER,
    "resting-heart-rate" INTEGER,
    "aerobic-threshold" INTEGER,
    "anaerobic-threshold" INTEGER,
    "vo2-max" INTEGER,
    "birthdate" DATE,
    "gender" VARCHAR(15),
    "first-name" VARCHAR(255),
    "last-name" VARCHAR(255),
    "member-id" VARCHAR(255),
    "polar-user-id" INTEGER,
    "registration-date" DATETIME,
    "extra-info-value" VARCHAR(1023),
    "extra-info-index" VARCHAR(1023),
    "extra-info-name" VARCHAR(1023)
);

-- Daily activity summaries table
CREATE TABLE daily_activity_summaries
(
    "active-calories" INTEGER,
    "active-steps" INTEGER,
    "calories" INTEGER,
    "created" DATETIME,
    "date" DATE,
    "duration" TIME,
    "id" INTEGER,
    "polar-user" VARCHAR(1023),
    "transaction-id" INTEGER
);

-- Exercise summaries table
CREATE TABLE exercise_summaries
(
    "calories" INTEGER,
    "detailed-sport-info" VARCHAR(255),
    "device" VARCHAR(255),
    "duration" TIME,
    "has-route" BOOLEAN,
    "heart-rate_average" INTEGER,
    "heart-rate_maximum" INTEGER,
    "id" INTEGER,
    "polar-user" VARCHAR(1023),
    "sport" VARCHAR(255),
    "start-time" DATETIME,
    "training-load" FLOAT,
    "transaction-id" INTEGER,
    "upload-time" DATETIME
);

-- Exercise heart zones table
CREATE TABLE exercise_heart_rate_zones
(
    "exercise_id" INTEGER,
    "in-zone" TIME,
    "index" INTEGER,
    "lower-limit" INTEGER,
    "upper-limit" INTEGER
);

-- Exerxise samples table
CREATE TABLE exercise_samples
(
    "id" INTEGER PRIMARY KEY,
    "exercise_id" INTEGER,
    "recording-rate" INTEGER,
    "sample-type" INTEGER,
    "data" FLOAT
);