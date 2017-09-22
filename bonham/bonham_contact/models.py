"""
Name: bonham  models 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version:  - 28.08.17 13:57 

"""

import logging

from bonham.bonham_core.models import Base, BaseModel

__all__ = ()

logger = logging.getLogger(__name__)


# start here
class Contact(BaseModel, Base):
    r"""Contact Model
    additional fields:
        :salute: String(20)
        :full_name: String(60)
    """


class Phone(BaseModel, Base):
    r"""PhoneNumber Model
    additional fields:
        :contact: ForeignKey('contact')
        :number: PhoneNumber -> number=PhoneNumber('0401234567', 'FI')
        :type: ChoiceType(PhoneType, impl=sa.Integer())
    """
