"""Builds the current robot model = body v3.34 (models/twiglet_v3_v334.xml) with the head_assembly <inertial> and its group-3
collision box taken from a hair-series model (the wig candidate on the hair base body).
This is valid because the hair pipeline (mk_head_wig.py / wig_inertial35.py) changes ONLY those two elements, and the head_assembly
body of its base model (models/twiglet_v3_head330rd_0.045.xml) is byte-identical to the head_assembly body in twiglet_v3_v334.xml.
The script checks both before it writes anything. The visual wig mesh stays the v3.30 one (visual only).
usage: python tools/make_v334_wig.py [hair_model.xml] [out.xml]
default: models/hair_c14_v344.xml (wig v3.44 c14) -> models/twiglet_v3_v334_wig344.xml
(the previous model, wig v3.40: python tools/make_v334_wig.py hair_y2_v340.xml twiglet_v3_v334_wig340.xml)"""
import os, sys, xml.etree.ElementTree as ET
M = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
src = sys.argv[1] if len(sys.argv) > 1 else "hair_c14_v344.xml"; dst = sys.argv[2] if len(sys.argv) > 2 else "twiglet_v3_v334_wig344.xml"
def head(T): return [b for b in T.iter("body") if b.get("name") == "head_assembly"][0]
body, base, hair = (ET.parse(os.path.join(M, f)) for f in ("twiglet_v3_v334.xml", "twiglet_v3_head330rd_0.045.xml", src))
assert ET.tostring(head(body)) == ET.tostring(head(base)), "head_assembly of v3.34 differs from the hair base model"
def strip(T):
    h = head(T); h = ET.fromstring(ET.tostring(h)); h.remove(h.find("inertial"))
    for g in [g for g in h.findall("geom") if g.get("type") == "box" and g.get("group") == "3"]: h.remove(g)
    return ET.tostring(h)
assert strip(base) == strip(hair), f"{src}: head_assembly differs from the base in more than the inertial + collision box"
hb, hh = head(body), head(hair)
ib, ih = hb.find("inertial"), hh.find("inertial"); ib.attrib.clear(); ib.attrib.update(ih.attrib)
cb = [g for g in hb.findall("geom") if g.get("type") == "box" and g.get("group") == "3"]; ch = [g for g in hh.findall("geom") if g.get("type") == "box" and g.get("group") == "3"]
assert len(cb) == len(ch) == 1; cb[0].attrib.clear(); cb[0].attrib.update(ch[0].attrib)
body.write(os.path.join(M, dst)); print("wrote models/" + dst, ih.attrib["mass"], "kg head")
