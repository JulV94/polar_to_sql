-- Physical information table
CREATE TABLE physical_information
(
    "created" DATETIME,
    "height" FLOAT,
    "id" INTEGER,
    "polar-user" VARCHAR(1023),
    "transaction-id" INTEGER,
    "weight" FLOAT,
    "weight-source" VARCHAR(255)
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
    "exercise_id" INTEGER,
    "recording-rate" INTEGER,
    "sample-type" INTEGER,
    "data" FLOAT
);