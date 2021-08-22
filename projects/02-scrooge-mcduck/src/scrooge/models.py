from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Stonk(Base):
    __tablename__ = 'stonks'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    prices = relationship('Price', order_by='desc(Price.ts)', back_populates='stonk', lazy='dynamic')

    def __repr__(self):
        return f'<Stonk(name="{self.name}", symbol="{self.symbol}", exchange="{self.exchange}")>'


class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    stonk_id = Column(Integer, ForeignKey('stonks.id'), nullable=False)
    stonk = relationship('Stonk', back_populates='prices')

    def __repr__(self):
        return f'<Price(stonk="{self.stonk.symbol}", bid="{self.bid}", ask="{self.ask}")>'
