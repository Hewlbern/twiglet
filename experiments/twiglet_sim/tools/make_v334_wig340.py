"""Builds models/twiglet_v3_v334_wig340.xml = body v3.34 (models/twiglet_v3_v334.xml) with the head_assembly <inertial> and its
group-3 collision box taken from the hair v3.40 model (models/hair_y2_v340.xml).
This is valid because the hair worker's mk_head_wig.py changes ONLY those two elements, and the head_assembly body of
its base model (body-v3.30/simC/twiglet_v3_head330rd_0.045.xml = models/twiglet_v3_head330rd_0.045.xml) is byte-identical to the
head_assembly body in twiglet_v3_v334.xml. This script checks that before it writes anything. The visual wig mesh stays the v3.30 one (visual only).
usage: python tools/make_v334_wig340.py"""
import os, xml.etree.ElementTree as ET
M = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
def head(T): return [b for b in T.iter("body") if b.get("name") == "head_assembly"][0]
body, base, hair = (ET.parse(os.path.join(M, f)) for f in ("twiglet_v3_v334.xml", "twiglet_v3_head330rd_0.045.xml", "hair_y2_v340.xml"))
assert ET.tostring(head(body)) == ET.tostring(head(base)), "head_assembly of v3.34 differs from the hair base model"
hb, hh = head(body), head(hair)
ib, ih = hb.find("inertial"), hh.find("inertial"); ib.attrib.clear(); ib.attrib.update(ih.attrib)
cb = [g for g in hb.findall("geom") if g.get("type") == "box" and g.get("group") == "3"]; ch = [g for g in hh.findall("geom") if g.get("type") == "box" and g.get("group") == "3"]
assert len(cb) == len(ch) == 1; cb[0].attrib.clear(); cb[0].attrib.update(ch[0].attrib)
body.write(os.path.join(M, "twiglet_v3_v334_wig340.xml")); print("wrote models/twiglet_v3_v334_wig340.xml", ih.attrib["mass"], "kg head")
