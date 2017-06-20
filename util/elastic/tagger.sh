cd harvester
python tagger.py --genes CCND1 CDKN2A CHEK1 DDR2 FGF19 FGF3 FGF4 FGFR1 IDO1 IDO2 MDM4 RAD51D  --tag_property tags --tag_name GS1
python tagger.py --genes CDKN2A PTEN TP53 SMAD4 KRAS --tag_property  tags --tag_name GS2
python tagger.py --genes \*  --tag_property  tags --tag_name ALL
python tagger.py --tag_property tags --tag_name SMMART \
--query "Olaparib Folfox Pembrolizumab Palbociclib ATRA Afatinib Vorinostat Everolimus Trametinib Cabozantinib Lenvatinib Ponatinib Ipilimumab Nivolumab Pertuzumab Carboplatin Enzalutamide Abiraterone Vemurafenib Cabazitaxel Panobinostat Imatinib Dasatinib Sunitinib Sorafenib Ruxolotinib Bortezomib Idelalisib Venetoclax Sirolimus Bevacizumab Erlotinib Celecoxib"
python tagger.py --tag_property dev-tags --tag_name no-location --query "NOT _exists_:feature.start"
python tagger.py --tag_property dev-tags --tag_name no-biomarker_type --query "NOT _exists_:feature.biomarker_type"
