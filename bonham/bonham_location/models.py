"""
Name: bonham  models 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version:  - 28.08.17 13:04 

"""

import logging

from bonham.bonham_core.models import Base, BaseModel

__all__ = ()

logger = logging.getLogger(__name__)


# start here

class Country(BaseModel, Base):
    r"""Country Model
    additional fields:
        :name: CountryType
        :area:
    """


class Address(BaseModel, Base):
    r"""Address Model
    additional fields:
        :addition: String(80)
        :street: String(100)
        :street_number: String(20)
        :zip_code: SmallInteger
        :city: String(80)
        :country: ForeignKey('country')
    """


class Location(BaseModel, Base):
    r"""Location Model
    additional fields:
        :name: String(60)
        :short_description: String(120)
        :address: ForeignKey('address')
        :
    """
