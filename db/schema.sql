-- Copyright © 2015 Jeffrey Meyers
-- This program is released under the "MIT License".
-- Please see the file COPYING in the source
-- distribution of this software for license terms.

--
-- Temporarily stores On Scans
-- Is sorted by date and joined by UUID to link to Off Scan
--
CREATE TABLE on_temp (
    id integer NOT NULL,
    uuid text,
    date timestamp without time zone,
    line text,
    dir text,
    match boolean,
    geom geometry(Point,2913),
    user_id integer NOT NULL
);

CREATE SEQUENCE on_temp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE on_temp_id_seq OWNED BY on_temp.id;
ALTER TABLE ONLY on_temp ALTER COLUMN id SET DEFAULT nextval('on_temp_id_seq'::regclass);
ALTER TABLE ONLY on_temp
    ADD CONSTRAINT on_temp_pkey PRIMARY KEY (id);
CREATE INDEX idx_on_temp_geom ON on_temp USING gist (geom);

--
-- Temporarily stores Off Scans
-- Not required, used for debugging
--
CREATE TABLE off_temp (
    id integer NOT NULL,
    uuid text,
    date timestamp without time zone,
    line text,
    dir text,
    match boolean,
    geom geometry(Point,2913),
    user_id integer NOT NULL
);

CREATE SEQUENCE off_temp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE off_temp_id_seq OWNED BY off_temp.id;
ALTER TABLE ONLY off_temp ALTER COLUMN id SET DEFAULT nextval('off_temp_id_seq'::regclass);
ALTER TABLE ONLY off_temp
    ADD CONSTRAINT off_temp_pkey PRIMARY KEY (id);
CREATE INDEX idx_off_temp_geom ON off_temp USING gist (geom);

--
-- Stores final On-Off scans that are linked up
-- Data is copied from temp tables
--
CREATE TABLE scans (
    id integer NOT NULL,
    date timestamp without time zone,
    line text,
    dir text,
    geom geometry(Point,2913),
    user_id integer NOT NULL
);

CREATE SEQUENCE scans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE scans_id_seq OWNED BY scans.id;
ALTER TABLE ONLY scans ALTER COLUMN id SET DEFAULT nextval('scans_id_seq'::regclass);
ALTER TABLE ONLY scans
    ADD CONSTRAINT scans_pkey PRIMARY KEY (id);
CREATE INDEX idx_scans_geom ON scans USING gist (geom);

--
-- Stores primary key for on-off pairs
-- Used for Bus routes
--
CREATE TABLE on_off_pairs__scans (
    id integer NOT NULL,
    on_id integer NOT NULL,
    off_id integer NOT NULL
);

CREATE SEQUENCE on_off_pairs__scans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE on_off_pairs__scans_id_seq OWNED BY on_off_pairs__scans.id;
ALTER TABLE ONLY on_off_pairs__scans ALTER COLUMN id SET DEFAULT nextval('on_off_pairs__scans_id_seq'::regclass);
ALTER TABLE ONLY on_off_pairs__scans
    ADD CONSTRAINT on_off_pairs__scans_pkey PRIMARY KEY (id);

--
-- Stores on-off stops that were selected from map
-- Used for MAX and Streetcar routes
--
CREATE TABLE on_off_pairs__stops (
    id integer NOT NULL,
    date timestamp without time zone,
    line text,
    dir text,
    on_stop integer NOT NULL,
    off_stop integer NOT NULL,
    user_id integer NOT NULL
);

CREATE SEQUENCE on_off_pairs__stops_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE on_off_pairs__stops_id_seq OWNED BY on_off_pairs__stops.id;
ALTER TABLE ONLY on_off_pairs__stops ALTER COLUMN id SET DEFAULT nextval('on_off_pairs__stops_id_seq'::regclass);
ALTER TABLE ONLY on_off_pairs__stops
    ADD CONSTRAINT on_off_pairs__stops_pkey PRIMARY KEY (id);

--
-- Stores Survey User information
-- Can be expaned to include more information
--
CREATE TABLE users (
    id integer NOT NULL,
    first text,
    last text,
    username text,
    password_hash text
);

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE users_id_seq OWNED BY users.id;
ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_unique_username UNIQUE (username);

--
-- Contains stop information for all TriMet stops
-- populated via shapefile using shp2pgsql
--

CREATE TABLE stops (
    gid integer NOT NULL,
    rte smallint,
    dir smallint,
    rte_desc character varying(50),
    dir_desc character varying(50),
    stop_seq integer,
    stop_id integer,
    stop_name character varying(50),
    geom geometry(Point,2913)
);

CREATE SEQUENCE stops_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE stops_gid_seq OWNED BY stops.gid;
ALTER TABLE ONLY stops ALTER COLUMN gid SET DEFAULT nextval('stops_gid_seq'::regclass);
ALTER TABLE ONLY stops
    ADD CONSTRAINT stops_pkey PRIMARY KEY (gid);
CREATE INDEX stops_geom_gist ON stops USING gist (geom);

--
-- Foreign Key Constrains
--

-- on_temp
ALTER TABLE ONLY on_temp
    ADD CONSTRAINT on_temp_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

-- off_temp
ALTER TABLE ONLY off_temp
    ADD CONSTRAINT off_temp_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

-- scans
ALTER TABLE ONLY scans
    ADD CONSTRAINT scans_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

-- on_off_pairs__scans
ALTER TABLE ONLY on_off_pairs__scans
    ADD CONSTRAINT on_off_pairs__scans_off_id_fkey FOREIGN KEY (off_id) REFERENCES scans(id);
ALTER TABLE ONLY on_off_pairs__scans
    ADD CONSTRAINT on_off_pairs__scans_on_id_fkey FOREIGN KEY (on_id) REFERENCES scans(id);

-- on_off_pairs__stops
ALTER TABLE ONLY on_off_pairs__stops
    ADD CONSTRAINT on_off_pairs__stops_off_stop_fkey FOREIGN KEY (off_stop) REFERENCES stops(gid);
ALTER TABLE ONLY on_off_pairs__stops
    ADD CONSTRAINT on_off_pairs__stops_on_stop_fkey FOREIGN KEY (on_stop) REFERENCES stops(gid);
ALTER TABLE ONLY on_off_pairs__stops
    ADD CONSTRAINT on_off_pairs__stops_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


