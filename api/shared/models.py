from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

import constants as cons


"""
Database Models
"""
Base = declarative_base()

class Scans(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = Column(Text)
    stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    stop_key = relationship("Stops", foreign_keys=stop)

    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.date = kwargs[cons.DATE]
        self.line = kwargs[cons.LINE]
        self.dir = kwargs[cons.DIR]
        self.geom = kwargs[cons.GEOM]
        self.user_id = kwargs[cons.USER_ID]
        self.stop = kwargs[cons.STOP]

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r >' %\
            (self.id, self.date, self.line, self.dir)


class OnOffPairs_Scans(Base):
    __tablename__ = 'on_off_pairs__scans'
    id = Column(Integer, primary_key = True)
    on_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    off_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    on = relationship("Scans", foreign_keys=on_id)
    off = relationship("Scans", foreign_keys=off_id)

    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.on_id = kwargs[cons.ON_ID]
        self.off_id = kwargs[cons.OFF_ID]

    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_id, self.off_id)


class OnOffPairs_Stops(Base):
    __tablename__ = 'on_off_pairs__stops'
    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    on_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    off_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    on = relationship("Stops", foreign_keys=on_stop)
    off = relationship("Stops", foreign_keys=off_stop)
    user_id = Column(Text)


    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.date = kwargs[cons.DATE]
        self.line = kwargs[cons.LINE]
        self.dir = kwargs[cons.DIR]
        self.on_stop = kwargs[cons.ON_STOP]
        self.off_stop = kwargs[cons.OFF_STOP]
        self.user_id = kwargs[cons.USER_ID]


    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_stop, self.off_stop)


class Stops(Base):
    __tablename__ = 'tm_route_stops'
    gid = Column(Integer, primary_key = True)
    rte = Column(SmallInteger)
    rte_desc = Column(Text)
    dir = Column(SmallInteger)
    dir_desc = Column(Text)
    stop_name = Column(Text)
    stop_seq = Column(Integer)
    stop_id = Column(Integer)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))

    def __repr__(self):
        return '<Stops: %r %r>' % (self.stop_id, self.stop_name)


class Routes(Base):
    __tablename__ = 'tm_routes'
    gid = Column(Integer, primary_key = True)
    rte = Column(SmallInteger)
    dir = Column(SmallInteger)
    rte_desc = Column(Text)
    public_rte = Column(Text)
    dir_desc = Column(Text)
    frequent = Column(Text) 
    type = Column(Text)
    geom = Column(Geometry(geometry_type='MULTILINESTRING', srid=2913))

    def __repr__(self):
        return '<Routes: %r %r>' % (self.rte, self.rte_desc)


class SurveysCore(Base):
    __tablename__ = 'tri_met_pilot_core' 
    uri = Column(String, primary_key = True)
    user = Column(String)
    mark_complete = Column(DateTime)
    submission_date = Column(DateTime)
    deviceid = Column(Text)
    start = Column(DateTime)
    end = Column(DateTime)
    english = Column(Text)
    other_lng = Column(Text)
    rte = Column(Text)
    dir = Column(Text)
    orig_purpose = Column(Text)
    orig_purpose_other = Column(Text)
    orig_lat = Column(Numeric)
    orig_lng = Column(Numeric)
    orig_geom = Column(Geometry(geometry_type='POINT', srid=2913))
    orig_access = Column(Text)
    orig_access_other = Column(Text)
    orig_blocks = Column(Text)
    orig_parking = Column(Text)
    dest_purpose = Column(Text)
    dest_purpose_other = Column(Text)
    dest_lat = Column(Numeric)
    dest_lng = Column(Numeric)
    dest_geom = Column(Geometry(geometry_type='POINT', srid=2913))
    dest_access = Column(Text)
    dest_access_other = Column(Text)
    dest_blocks = Column(Integer)
    dest_parking = Column(Text)
    board_id = Column(Integer)
    alight_id = Column(Integer)
    board_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=True)
    alight_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=True)
    board = relationship("Stops", foreign_keys=board_stop)
    alight = relationship("Stops", foreign_keys=alight_stop)
    transfers_before = Column(Text)
    tb_1 = Column(Text)
    tb_2 = Column(Text)
    tb_3 = Column(Text)
    transfers_after = Column(Text)
    ta_1 = Column(Text)
    ta_2 = Column(Text)
    ta_3 = Column(Text)
    churn = Column(Text)
    churn_other = Column(Text)
    reason = Column(Text)
    license = Column(Text)
    house_no = Column(Integer)
    wrk_out_house = Column(Integer)
    wrk_vchl = Column(Integer)
    race = Column(Text)
    race_other = Column(Text)
    income = Column(Text)
    addit_lng = Column(Text)
    other_lng_other = Column(Text)
    english_prof = Column(Text)
    valid = Column(Integer)

    def __init__(self, **kwargs):
        self.uri = kwargs[cons.URI]
        self.user = kwargs[cons.USER]
        self.mark_complete = kwargs[cons.MARK_COMPLETE]
        self.submission_date = kwargs[cons.SUBMISSION_DATE]
        self.deviceid = kwargs[cons.DEVICEID]
        self.start = kwargs[cons.START]
        self.end = kwargs[cons.END]
        self.english = kwargs[cons.ENGLISH]
        self.other_lng = kwargs[cons.OTHER_LNG]
        self.rte = kwargs[cons.RTE]
        self.dir = kwargs[cons.DIR]
        self.orig_purpose = kwargs[cons.ORIG_PURPOSE]
        self.orig_purpose_other = kwargs[cons.ORIG_PURPOSE_OTHER]
        self.orig_lat = kwargs[cons.ORIG_LAT]
        self.orig_lng = kwargs[cons.ORIG_LNG]
        self.orig_geom = kwargs[cons.ORIG_GEOM]
        self.orig_access = kwargs[cons.ORIG_ACCESS]
        self.orig_access_other = kwargs[cons.ORIG_ACCESS_OTHER]
        self.orig_blocks = kwargs[cons.ORIG_BLOCKS]
        self.orig_parking = kwargs[cons.ORIG_PARKING]
        self.dest_purpose = kwargs[cons.DEST_PURPOSE]
        self.dest_purpose_other = kwargs[cons.DEST_PURPOSE_OTHER]
        self.dest_lat = kwargs[cons.DEST_LAT]
        self.dest_lng = kwargs[cons.DEST_LNG]
        self.dest_geom = kwargs[cons.DEST_GEOM]
        self.dest_access = kwargs[cons.DEST_ACCESS]
        self.dest_access_other = kwargs[cons.DEST_ACCESS_OTHER]
        self.dest_blocks = kwargs[cons.DEST_BLOCKS]
        self.dest_parking = kwargs[cons.DEST_PARKING]
        self.board_id = kwargs[cons.BOARD_ID]
        self.alight_id = kwargs[cons.ALIGHT_ID]
        self.board_stop = kwargs[cons.BOARD_STOP]
        self.alight_stop = kwargs[cons.ALIGHT_STOP] 
        self.transfers_before = kwargs[cons.TRANSFERS_BEFORE]
        self.tb_1 = kwargs[cons.TB_1]
        self.tb_2 = kwargs[cons.TB_2]
        self.tb_3 = kwargs[cons.TB_3]
        self.transfers_after = kwargs[cons.TRANSFERS_AFTER]
        self.ta_1 = kwargs[cons.TA_1]
        self.ta_2 = kwargs[cons.TA_2]
        self.ta_3 = kwargs[cons.TA_3]
        self.churn = kwargs[cons.CHURN]
        self.churn_other = kwargs[cons.CHURN_OTHER]
        self.reason = kwargs[cons.REASON]
        self.license = kwargs[cons.LICENSE]
        self.house_no = kwargs[cons.HOUSE_NO]
        self.wrk_out_house = kwargs[cons.WRK_OUT_HOUSE]
        self.wrk_vchl = kwargs[cons.WRK_VCHL]
        self.race = kwargs[cons.RACE]
        self.race_other = kwargs[cons.RACE_OTHER]
        self.income = kwargs[cons.INCOME]
        self.addit_lng = kwargs[cons.ADDIT_LNG]
        self.other_lng_other = kwargs[cons.OTHER_LNG_OTHER]
        self.english_prof = kwargs[cons.ENGLISH_PROF]
        self.valid = kwargs[cons.VALID]

class SurveysLng(Base):
    __tablename__ = 'tri_met_pilot_other_lngs'
    uri = Column(String, primary_key = True)
    parent_uri = Column(String, ForeignKey("tri_met_pilot_core.uri"), nullable=False)
    parent = relationship("SurveysCore", foreign_keys=parent_uri)
    value = Column(Text)

    def __init__(self, **kwargs):
        self.uri = kwargs[cons.URI]
        self.parent_uri = kwargs[cons.PARENT_URI]
        self.value = kwargs[cons.VALUE]


