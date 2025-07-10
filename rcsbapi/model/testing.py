# Compare two CIF data containers


# from rcsb.utils.io.MarshalUtil import MarshalUtil
# mU=MarshalUtil()

# containerList1=mU.doImport('old.cif',fmt='mmcif')
# containerList2=mU.doImport('new.cif',fmt='mmcif')

# c1 = containerList1[0]
# c2 = containerList2[0]

# for cat in c1.getObjNameList():
#     for attr in c1.getObj(cat).getAttributeList():
#         c1AttrL = c1.getObj(cat).getAttributeValueList(attr)
#         c2AttrL = c2.getObj(cat).getAttributeValueList(attr)
#         c1AttrTypedL = []
#         c2AttrTypedL = []
#         if len(c2AttrL) > 0:
#             for i, _ in enumerate(c2AttrL):
#                 if isinstance(c2AttrL[i], float):
#                     c1AttrTypedL.append(float(c1AttrL[i]))
#                     c2AttrTypedL.append(float(c2AttrL[i]))
#                 elif isinstance(c2AttrL[i], int):
#                     c1AttrTypedL.append(int(c1AttrL[i]))
#                     c2AttrTypedL.append(int(c2AttrL[i]))
#                 else:
#                     c1AttrTypedL.append(str(c1AttrL[i]).replace(".", "?"))  # These may be swapped between mmCIF and BCIF
#                     c2AttrTypedL.append(str(c2AttrL[i]).replace(".", "?"))
#         matchOk = c1AttrTypedL == c2AttrTypedL
#         if not matchOk:
#             print(f"Category and attribute translation mismatch {cat} {attr}: {c1AttrTypedL} (c1) vs. {c2AttrTypedL} (c2)")



### OR - more concise non-typing version: ###

from rcsb.utils.io.MarshalUtil import MarshalUtil
mU=MarshalUtil()

containerList1 = mU.doImport('C:/Users/Krish/Documents/gitRCSB/py-rcsb-api/1tqn_full.bcif', fmt='bcif')
containerList2 = mU.doImport('C:/Users/Krish/Documents/gitRCSB/py-rcsb-api/1tqn_full(1).bcif', fmt='bcif')

c1 = containerList1[0]
c2 = containerList2[0]

for cat in c1.getObjNameList():
    for attr in c1.getObj(cat).getAttributeList():
        c1AttrL = c1.getObj(cat).getAttributeValueList(attr)
        c2AttrL = c2.getObj(cat).getAttributeValueList(attr)
        matchOk = c1AttrL == c2AttrL
        if not matchOk:
            print(f"Category and attribute translation mismatch {cat} {attr}: {c1AttrL} (c1) vs. {c2AttrL} (c2)")
