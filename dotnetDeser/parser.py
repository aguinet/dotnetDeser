from construct import Struct, Int8ul, Int32ul, this, VarInt, Peek, Enum, Byte, Bytes, Switch, GreedyRange, Array, Construct, ListContainer, Int16ul, Int64ul, RepeatUntil, Int16sl, Int32sl, Int64sl, Flag, If, Computed, LazyBound
import functools
import operator

# https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-nrbf/954a0657-b901-4813-9398-4ec732fe8b32
RecordTypeEnum = Enum(Byte,
    SerializedStreamHeader=0,
    ClassWithId=1,
    SystemClassWithMembers=2,
    ClassWithMembers=3,
    SystemClassWithMembersAndTypes=4,
    ClassWithMembersAndTypes=5,
    BinaryObjectString=6,
    BinaryArray=7,
    MemberPrimitiveTyped=8,
    MemberReference=9,
    ObjectNull=10,
    MessageEnd=11,
    BinaryLibrary=12,
    ObjectNullMultiple256=13,
    ObjectNullMultiple=14,
    ArraySinglePrimitive=15,
    ArraySingleObject=16,
    ArraySingleString=17,
    MethodCall=21,
    MethodReturn=22)

LengthPrefixedString = Struct(
        "len" / VarInt,
        "data" / Bytes(this.len))

ClassInfo = Struct(
    "ObjectId" / Int32ul,
    "Name" / LengthPrefixedString,
    "MemberCount" / Int32ul,
    "MemberNames" / Array(this.MemberCount, LengthPrefixedString))

BinaryTypeEnumeration = Enum(Byte,
    Primitive=0,
    String=1,
    Object=2,
    SystemClass=3,
    Class=4,
    ObjectArray=5,
    StringArray=6,
    PrimitiveArray=7)

PrimitiveTypeEnumeration = Enum(Byte,
    Boolean=1,
    Byte=2,
    Char=3,
    Decimal=5,
    Double=6,
    Int16=7,
    Int32=8,
    Int64=9,
    SByte=10,
    Single=11,
    TimeSpan=12,
    DateTime=13,
    UInt16=14,
    UInt32=15,
    UInt64=16,
    Null=17,
    String=18)

DateTime = Struct(
    "Value" / Int64ul)

PrimitiveTypeParsers = {
    PrimitiveTypeEnumeration.Boolean: Flag,
    PrimitiveTypeEnumeration.Byte: Byte,
    PrimitiveTypeEnumeration.Int16: Int16sl,
    PrimitiveTypeEnumeration.Int32: Int32sl,
    PrimitiveTypeEnumeration.Int64: Int64sl,
    PrimitiveTypeEnumeration.UInt16: Int16ul,
    PrimitiveTypeEnumeration.UInt32: Int32ul,
    PrimitiveTypeEnumeration.UInt64: Int64ul,
    PrimitiveTypeEnumeration.DateTime: DateTime
}

ClassTypeInfo = Struct(
    "TypeName" / LengthPrefixedString,
    "LibraryId" / Int32ul)

class AddInfos(Construct):
    def _parse(self, stream, context, path):
        bins_ = context.BinaryTypeEnums
        d = {
            BinaryTypeEnumeration.PrimitiveArray: PrimitiveTypeEnumeration,
            BinaryTypeEnumeration.Primitive: PrimitiveTypeEnumeration,
            BinaryTypeEnumeration.Class: ClassTypeInfo,
            BinaryTypeEnumeration.SystemClass: LengthPrefixedString
        }
        ret = []
        for b in bins_:
            p = d.get(b, None)
            if p is None: continue
            ret.append(p._parse(stream, context, path))
        return ListContainer(ret)

    def _build(self, obj, stream, context, path):
        fds

    def _sizeof(self, context, path):
        raise SizeofError()

class MemberValues(Construct):
    _allClses = {}

    def __init__(self, relativeToId):
        super().__init__()
        self._relativeToId = relativeToId

    def _parse(self, stream, context, path):
        allClses = self._allClses
        if not self._relativeToId:
            types_ = context.MemberTypeInfo.BinaryTypeEnums
            infos = context.MemberTypeInfo.Infos
            allClses[context.ClassInfo.ObjectId] = (types_,infos)
        else:
            types_, infos = allClses[context.MetadataId]
        hasExtraInfos = (
            BinaryTypeEnumeration.PrimitiveArray,
            BinaryTypeEnumeration.Primitive,
            BinaryTypeEnumeration.Class,
            BinaryTypeEnumeration.SystemClass)
        ret = []
        idxInfos = 0
        for ty in types_:
            info = None
            if ty in hasExtraInfos:
                info = infos[idxInfos]
                idxInfos += 1
            ret.append(self.parse_value(ty, info, stream, context, path))
        return ListContainer(ret)

    def parse_value(self, ty, info, stream, context, path):
        d = {
            BinaryTypeEnumeration.Primitive: self.parse_primitive,
            BinaryTypeEnumeration.Class: self.parse_cls,
            BinaryTypeEnumeration.SystemClass: self.parse_cls,
            BinaryTypeEnumeration.String: self.parse_cls,
            BinaryTypeEnumeration.PrimitiveArray: self.parse_cls,
        }
        p = d[ty]
        return p(info, stream, context, path)

    def parse_primitive(self, info, stream, context, path):
        p = PrimitiveTypeParsers[info]
        return p._parse(stream, context, path)

    def parse_cls(self, info, stream, context, path):
        return Record._parse(stream, context, path)

    def _build(self, obj, stream, context, path):
        fds

    def _sizeof(self, context, path):
        raise SizeofError()

class SystemMemberValues(Construct):
    _allClses = {}

    def __init__(self):
        super().__init__()

    def _parse(self, stream, context, path):
        count = context.ClassInfo.MemberCount
        print("count")
        for i in range(count):
            ret.append(Record._parse(stream, contextn, path))
        return ListContainer(ret)

MemberTypeInfo = Struct(
    "BinaryTypeEnums" / Array(this._.ClassInfo.MemberCount, BinaryTypeEnumeration),
    "Infos" / AddInfos())

# Arrays
ArrayInfo = Struct(
    "ObjectId" / Int32ul,
    "Length" / Int32ul)

ArraySinglePrimitive = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ArrayInfo" / ArrayInfo,
    "PrimitiveTypeEnum" / PrimitiveTypeEnumeration,
    "Values" / Switch(this.PrimitiveTypeEnum, {k: Array(this.ArrayInfo.Length, v) for k,v in PrimitiveTypeParsers.items()}))

BinaryArrayTypeEnumeration = Enum(Byte,
    Single=0,
    Jagged=1,
    Rectangular=2,
    SingleOffset=3,
    JaggedOffset=4,
    RectangularOffset=5)

BinaryArray = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ObjectId" / Int32ul,
    "BinaryArrayTypeEnum" / BinaryArrayTypeEnumeration,
    "Rank" / Int32ul,
    "Lengths" / Array(this.Rank, Int32ul),
    "LowerBounds" / If(this.BinaryArrayTypeEnum == BinaryArrayTypeEnumeration.SingleOffset or this.BinaryArrayTypeEnum == BinaryArrayTypeEnumeration.JaggedOffset or this.BinaryArrayTypeEnum == BinaryArrayTypeEnumeration.RectangularOffset, Array(this.Rank, Int32sl)),
    "TypeEnum" / BinaryTypeEnumeration,
    "Infos" / Switch(this.TypeEnum, {
        BinaryTypeEnumeration.Primitive: PrimitiveTypeEnumeration,
        BinaryTypeEnumeration.SystemClass: LengthPrefixedString,
        BinaryTypeEnumeration.Class: ClassTypeInfo,
        BinaryTypeEnumeration.PrimitiveArray: PrimitiveTypeEnumeration},
        default=None),
    "CountElts" / Computed(lambda ctx: functools.reduce(operator.mul, ctx.Lengths, 1)),
    "Values" / Array(this.CountElts, Switch(this.TypeEnum, {
            BinaryTypeEnumeration.Primitive: Switch(this.Infos, PrimitiveTypeParsers),
            BinaryTypeEnumeration.String: LengthPrefixedString,
            BinaryTypeEnumeration.PrimitiveArray: LazyBound(lambda: Record),
            BinaryTypeEnumeration.Class: LazyBound(lambda: Record),
            BinaryTypeEnumeration.SystemClass: LazyBound(lambda: Record),
        })))


# Records
SerializationHeaderRecord = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "RootId" / Int32ul,
    "HeaderId" / Int32ul,
    "MajorVersion" / Int32ul,
    "MinorVersion" / Int32ul)

BinaryObjectString = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ObjectId" / Int32ul,
    "Value" / LengthPrefixedString)

BinaryLibrary = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "LibraryId" / Int32ul,
    "LibraryName" / LengthPrefixedString)

ClassWithMembersAndTypes = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ClassInfo" / ClassInfo,
    "MemberTypeInfo" / MemberTypeInfo,
    "LibraryId" / Int32ul,
    "Values" / MemberValues(False))

SystemClassWithMembers = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ClassInfo" / ClassInfo,
    "Values" / SystemMemberValues()
)

MemberReference = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "IdRef" / Int32ul)

MemberPrimitiveTyped = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "PrimitiveTypeEnum" / PrimitiveTypeEnumeration,
    "Value" / Switch(this.PrimitiveTypeEnum, PrimitiveTypeParsers))

ClassWithId = Struct(
    "RecordTypeEnum" / RecordTypeEnum,
    "ObjectId" / Int32ul,
    "MetadataId" / Int32ul,
    "Values" / MemberValues(True))

ObjectNull = Struct(
    "RecordTypeEnum" / RecordTypeEnum)


Record = Struct(
    "RecordTypeEnum" / Peek(RecordTypeEnum),
    "Obj" / Switch(this.RecordTypeEnum, {
        RecordTypeEnum.SerializedStreamHeader: SerializationHeaderRecord,
        RecordTypeEnum.BinaryObjectString: BinaryObjectString,
        RecordTypeEnum.BinaryLibrary: BinaryLibrary,
        RecordTypeEnum.ClassWithMembersAndTypes: ClassWithMembersAndTypes,
        RecordTypeEnum.MemberReference: MemberReference,
        RecordTypeEnum.SystemClassWithMembers: SystemClassWithMembers,
        RecordTypeEnum.ArraySinglePrimitive: ArraySinglePrimitive,
        RecordTypeEnum.ClassWithId: ClassWithId,
        RecordTypeEnum.ObjectNull: ObjectNull,
        RecordTypeEnum.BinaryArray: BinaryArray,
        RecordTypeEnum.MemberPrimitiveTyped: MemberPrimitiveTyped
        }
    ))

AllRecords = RepeatUntil(lambda obj,lst,ctx: obj.RecordTypeEnum == RecordTypeEnum.MessageEnd, Record)

def parse(data):
    MemberValues._allClses = {}
    return AllRecords.parse(data)
