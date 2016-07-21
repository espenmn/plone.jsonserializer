# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
# TODO: Once plone.app.textfield is compatible
# from plone.app.textfield.interfaces import IRichTextValue
from plone.jsonserializer.interfaces import IJsonCompatible
from zope.component import adapter
from zope.component.hooks import getSite
# TODO: from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import implementer
from zope.interface import Interface

# TODO: import Missing

try:
    unicode
except NameError:
    unicode = str

try:
    long
except NameError:
    long = int

try:
    from Products.CMFPlone.utils import safe_unicode
except ImportError:
    safe_unicode = str

try:
    from Products.CMFPlone.utils import getSiteEncoding
except ImportError:
    HAS_SITE = False
else:
    HAS_SITE = True

try:
    from DateTime import DateTime
except ImportError:
    HAS_ZOPE_DATETIME = False
else:
    HAS_ZOPE_DATETIME = True


def json_compatible(value):
    """The json_compatible function converts any value to JSON compatible
    data when possible, raising a TypeError for unsupported values.
    This is done by using the IJsonCompatible converters.

    Be aware that adapting the value `None` will result in a component
    lookup error unless `None` is passed in as default value.
    Because of that the `json_compatible` helper method should always be
    used for converting values that may be None.
    """
    return IJsonCompatible(value, None)


def encoding():
    if HAS_SITE:
        return getSiteEncoding(getSite())
    else:
        return 'utf-8'


@adapter(Interface)
@implementer(IJsonCompatible)
def default_converter(value):
    if value is None:
        return value

    if type(value) in (unicode, bool, int, float, long):
        return value

    raise TypeError(
        'No converter for making'
        ' {0!r} ({1}) JSON compatible.'.format(value, type(value)))


@adapter(str)
@implementer(IJsonCompatible)
def string_converter(value):
    return safe_unicode(value, )


@adapter(list)
@implementer(IJsonCompatible)
def list_converter(value):
    return list(map(json_compatible, value))


@adapter(PersistentList)
@implementer(IJsonCompatible)
def persistent_list_converter(value):
    return list_converter(value)


@adapter(tuple)
@implementer(IJsonCompatible)
def tuple_converter(value):
    return list(map(json_compatible, value))


@adapter(frozenset)
@implementer(IJsonCompatible)
def frozenset_converter(value):
    return list(map(json_compatible, value))


@adapter(set)
@implementer(IJsonCompatible)
def set_converter(value):
    return list(map(json_compatible, value))


@adapter(dict)
@implementer(IJsonCompatible)
def dict_converter(value):
    if value == {}:
        return {}

    keys, values = zip(*value.items())
    keys = map(json_compatible, keys)
    values = map(json_compatible, values)
    return dict(zip(keys, values))


@adapter(PersistentMapping)
@implementer(IJsonCompatible)
def persistent_mapping_converter(value):
    return dict_converter(value)


@adapter(datetime)
@implementer(IJsonCompatible)
def python_datetime_converter(value):
    if HAS_ZOPE_DATETIME:
        return json_compatible(DateTime(value))
    else:
        return json_compatible(value.isoformat())


if HAS_ZOPE_DATETIME:
    @adapter(DateTime)
    @implementer(IJsonCompatible)
    def zope_DateTime_converter(value):
        return json_compatible(value.ISO8601())


@adapter(date)
@implementer(IJsonCompatible)
def date_converter(value):
    return json_compatible(value.isoformat())


@adapter(time)
@implementer(IJsonCompatible)
def time_converter(value):
    return json_compatible(value.isoformat())


@adapter(timedelta)
@implementer(IJsonCompatible)
def timedelta_converter(value):
    return json_compatible(value.total_seconds())

# TODO: Once plone.app.textfield is compatible
# @adapter(IRichTextValue)
# @implementer(IJsonCompatible)
# def richtext_converter(value):
#     return {
#         u'data': json_compatible(value.raw),
#         u'content-type': json_compatible(value.mimeType),
#         u'encoding': json_compatible(value.encoding),
#     }


@adapter(Message)
@implementer(IJsonCompatible)
def i18n_message_converter(value):
    # TODO:
    # value = translate(value, context=getRequest())
    return value

# TODO
# @adapter(Missing.Value.__class__)
# @implementer(IJsonCompatible)
# def missing_value_converter(value):
#     return None
