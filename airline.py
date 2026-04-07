'''This module contains airline functions'''
__author__ = "jdanek"

import logging
import sqlite3
from pathlib import Path

# Init logger
logger = logging.getLogger("flight_tracks")

# default airline dictionary
airline_dict = {
    "AAL":"American", "DAL":"Delta", "UAL":"United", "CSN":"China Southern", "SWA":"Southwest", "CES":"China Eastern", "CCA":"Air China", "RYR":"Ryanair", "EZY":"EasyJet", "IGO":"IndiGo", "THY":"Turkish",
    "JBU":"JetBlue", "SKW":"SkyWest", "CSC":"Sichuan", "DLH":"Lufthansa", "CHH":"Hainan", "UAE":"Emirates", "KLM":"KLM", "BAW":"British Air", "FDX":"FedEx", "RPA":"Republic", "CSZ":"Shenzhen",
    "CXA":"XiamenAir", "TAM":"LATAM", "AIC":"Air India", "UPS":"UPS", "ACA":"Air Canada", "CPA":"Cathay Pacific", "AFR":"Air France", "KAL":"Korean Air", "CQH":"Spring", "SIA":"Singapore",
    "AZU":"Azul", "JAL":"Japan", "EDV":"Endeavor Air", "ENY":"Envoy Air", "EJA":"NetJets", "GLO":"GOL", "PGT":"Pegasus", "ANA":"All Nippon", "IBE":"Iberia", "AFL":"Aeroflot", "SVA":"Saudia",
    "CDG":"Shandong", "FFT":"Frontier", "VJC":"VietJet Air", "NKS":"Spirit", "SAS":"SAS", "QFA":"Qantas", "AXB":"Air India", "AVA":"Avianca", "CAL":"China", "JIA":"PSA", "SWR":"Swiss", "CDC":"Zhejiang",
    "EVA":"EVA Air", "FIN":"Finnair", "VLG":"Vueling", "EXS":"Jet2", "HVN":"Vietnam", "AXM":"AirAsia", "CXK":"ATP", "GCR":"Tianjin", "TOM":"TUI", "EWG":"Eurowings", "ASA":"Alaska", "AUA":"Austrian",
    "WJA":"WestJet", "TAP":"TAP Air", "CBJ":"Beijing", "MAS":"Malaysia", "UEA":"Chengdu", "WMT":"Wizz Air", "DKH":"Juneyao", "GTI":"Atlas Air", "WZZ":"Wizz Air", "ETH":"Ethiopian", "VIV":"VivaAerobus",
    "AIQ":"Air Asia", "CSH":"Shanghai", "CMP":"Copa", "THA":"Thai", "AAR":"Asiana", "LAN":"LATAM", "TGW":"Scoot", "VOI":"Volaris", "ARG":"Aerolineas", "AEE":"Aegean", "CHB":"West Air", "LKE":"Lucky Air",
    "CUA":"China United", "LOT":"LOT Polish", "LNK":"Airlink", "HXA":"China", "LXJ":"Flexjet", "BEL":"Brussels", "KNE":"Flynas", "CEB":"Cebu", "RYS":"Buzz", "LPE":"LATAM Peru", "NSZ":"Norwegian Air",
    "AMX":"AeroMéxico", "RLH":"Ruili", "NJE":"NetJets", "TBA":"Tibet", "PDT":"Piedmont", "ITY":"ITA", "JZA":"Jazz", "SBI":"S7", "TVF":"Transavia", "ETD":"Etihad", "POE":"Porter", "RAM":"Royal Air", 
    "PRO":"Propair", "MXY":"Breeze", "ICE":"Icelandair", "QTR":"Qatar", "VJT":"VistaJet", "TCT":"Transcontinental", "MSR":"Egypt Air", "EPA":"Donghai", "HKE":"Hong Kong", "CHX":"Hubschrauber", 
    "BTI":"Air Baltic", "HOP":"HOP", "ANZ":"Air New Zealand", "OMA":"Oman Air", "BPX":"Phoenix", "ERU":"Embry Riddle", "QDA":"Qingdao", "CBG":"GX", "ASH":"Mesa", "JYH":"9 Air", "TSC":"Air Transat", 
    "ANE":"Air Nostrum", "FDB":"FlyDubai", "TWB":"Tway Air", "CKS":"Kalitta Air", "EIN":"Aer Lingus", "VIR":"Virgin", "GCM":"Comair", "SEJ":"SpiceJet", "AHY":"Azerbaijan", "SFR":"Safair", "CFG":"Condor", 
    "CTV":"Citilink", "HBH":"Hebei", "NOZ":"Norwegian Air", "SJX":"Starlux", "LNI":"Lion Air", "BOX":"AeroLogic", "PHM":"Petroleum", "JJA":"Jeju Air", "AKJ":"Akasa Air", "PAL":"Philippine", "TRA":"Transavia", 
    "SDM":"Rossiya", "ABY":"Air Arabia", "VOZ":"Virgin", "RJA":"Royal Jordanian", "JES":"JetSMART", "DAH":"Air Algerie", "FBZ":"Flybondi", "JST":"Jetstar", "EDW":"Edelweiss Air", "KAP":"Cape Air", 
    "KQA":"Kenya", "CLX":"Cargolux", "TLM":"Thai Lion", "DLA":"Air Dolomiti", "LFA":"Aerosim", "ARE":"LATAM", "PSC":"Pascan", "OKA":"Okay", "CAO":"Air China", "SLI":"Aeroméxico", "KZR":"Air Astana", 
    "AWQ":"Indonesia Air", "ABX":"ABX Air", "SJV":"Super Air Jet", "MXD":"Malindo Air", "AAY":"Allegiant Air", "TVS":"Smartwings", "APJ":"Peach", "FAD":"flyadeal", "IBB":"Binter Canarias", "JNA":"Jin Air", 
    "ESR":"Eastarjet", "UCA":"CommuteAir", "OCN":"Discover", "SVR":"Ural", "KNA":"Kunming", "CGN":"Air Changan", "TCF":"FIT", "UZB":"Uzbekistan", "EFW":"Euroflyer", "CRK":"Hong Kong", "CGZ":"Colorful Guizhou", 
    "BPO":"Bundespolizei", "DEI":"Eco Air", "VTM":"Aeronaves", "TUI":"TuiFly", "FJI":"Fiji", "GIA":"Garuda Indonesia", "VSV":"SCAT", "ATN":"Air Transport", "PRJ":"Aero Servicios", "BTK":"Batik Air", 
    "SKY":"Skymark", "MEA":"MEA", "BTZ":"Bristow", "PIA":"Pakistan", "ROU":"Air Canada", "OZN":"Aviator Zone", "TVJ":"Vietjet Air", "GEC":"Lufthansa", "VTS":"Everts Air", "SCX":"Sun Country", "IBS":"Iberia", 
    "NIT":"Georgia State", "AKX":"ANA Wings", "JJP":"Jetstar", "CUH":"Urumqi Air", "TTW":"Tigerair", "WUK":"Wizz Air", "ELY":"El Al", "XAX":"AirAsia", "BKP":"Bangkok", "MSC":"Air Cairo", "LHX":"City", 
    "YZR":"Suparna", "SXA":"Southern Cross", "AIP":"Alpine", "CLH":"Lufthansa", "BCY":"Cityjet", "VOE":"Volotea", "CJT":"Cargojet", "EFY":"Clic Air", "AMF":"Ameriflight", "CKK":"China", "IRO":"Csa Air", 
    "RUK":"Ryanair", "SFY":"Skyborne", "JRE":"FlyExclusive", "CCD":"Dalian", "DEF":"AVDEF", "WEN":"WestJet", "OAW":"Helvetic", "OTC":"Air Travel", "CFE":"CityFlyer", "PSR":"Express", "JTA":"Japan", 
    "HAL":"Hawaiian", "PSA":"Pacific Island", "ENT":"Enter Air", "ROT":"TAROM", "MFX":"My Freighter", "FZA":"Fuzhou", "AMU":"Air Macau", "TKJ":"AJet", "BHA":"Buddha Air", "AZG":"Silk Way West", "PVL":"PAL", 
    "LVS":"Insignia", "OMS":"SalamAir", "CGH":"Air Guilin", "SAA":"South African", "GJS":"GoJet", "DEE":"Dixie", "ADY":"Air Arabia", "SPK":"Spectrum", "UTA":"UTair", "AZV":"Azur", "DHK":"DHL", "PBD":"Pobeda", 
    "LNE":"LATAM", "ECO":"ecojet", "EWL":"Eurowings", "MMA":"MAI", "TCA":"Tropican Air", "KII":"Kalitta", "SYS":"Shawbury", "PSS":"RKC", "ASL":"Air Serbia", "TAR":"Tunisair", "CSG":"China Southern", 
    "ALK":"SriLankan", "PTO":"North West", "AEA":"Air Europa", "SKU":"Sky Airline", "NOS":"Neos", "SNJ":"Solaseed", "ULR":"Ultimate Air", "AYN":"FlyArystan", "AIH":"AirZeta", "LRS":"SANSA", 
    "SPM":"Air Saint Pierre", "DER":"Deerjet", "AJX":"Air Japan", "MRA":"Martinaire", "NSE":"SATENA", "ACN":"Azul Conecta", "SXS":"Sun", "CNS":"Cobalt Air", "CSB":"21 Air", "SEH":"Sky", "GCI":"Italian CG", 
    "SFJ":"StarFlyer", "GBB":"Global", "DEN":"Denel", "EAI":"Emerald", "SPN":"Skorpion Air", "DWI":"Arajet", "TFL":"TUI", "SPR":"Provincial", "FLE":"Flair", "SDG":"Star Air", "BBC":"Bangladesh", 
    "ABL":"Air Busan", "LDA":"Lauda Europe", "GFD":"Gesellschaft", "SEU":"SkyUp", "SKX":"Sky Airline", "GAM":"German Army", "CNV":"US Navy", "BHL":"Bristow", "HKS":"CHC", "NBT":"Norse Atlantic", 
    "PRM":"Prime Air", "MTN":"Mountain Air", "FDY":"Southern", "WUP":"Wheels Up", "PST":"Air Panama", "TIB":"Trip Linhas", "MNB":"MNG", "SJO":"Spring Japan", "PSV":"Servicios Aereos", "NWS":"Nordwind", 
    "HLF":"Central", "KMM":"KM Malta", "SPT":"Bengis", "TAI":"Avianca", "FHM":"Freebird", "DES":"Chilcotin", "NOK":"Nok", "ATC":"Air Tanzania", "MOR":"Morefly", "GER":"German", "PAS":"Pelita Air", 
    "VJH":"VistaJet", "SLH":"Silverhawk", "DFL":"Avincis", "AJT":"Amerijet", "AZO":"Azimuth", "HLE":"First Air", "DMS":"Diamond Sky", "LGL":"Luxair", "FWI":"Air Caraïbes", "CTM":"Air Support", 
    "GPD":"Tradewind", "NOR":"Norsk", "EAG":"Emerald", "JAT":"JetSMART", "SRQ":"Cebgo", "PAT":"Army", "CRQ":"Air Creebec", "PRB":"Puerto Rico Air", "CTG":"Canadian CG", "LTA":"LIFT", "SZS":"Scandinavian", 
    "TZP":"ZIPAIR", "GEL":"Airline GeoSky", "MAC":"Air Arabia", "BRX":"Braathens", "PEG":"Pegasus", "RTO":"Arhabaev", "SPA":"Sierra Pacific", "RPB":"Copa Colombia", "SAM":"Special Air", "TWY":"Sunset", 
    "LSJ":"Air Liaison", "GBM":"GBM Aereo", "GBA":"Barrier Air", "FJL":"Fly Jinnah", "SIF":"Air Sial", "PTW":"Pattaya", "LRC":"Avianca", "FHY":"Freebird", "SJY":"Sriwijaya Air", "CGC":"Cal Gulf", "CSS":"SF", 
    "CAP":"USAFX", "JMA":"Jambojet", "GAC":"GlobeAir", "ASP":"AirSprint", "AKT":"Canadian North", "FRG":"Freight Runners", "RWZ":"Red Wings", "LLM":"Yamal", "NAK":"New Kazakstan", "SPQ":"Sun Phu Quoc", 
    "GAP":"PAL", "HYD":"Hydro-Quebec", "JAF":"TUI Fly", "ADO":"Air Do", "MAE":"Maersk", "BRU":"Belavia", "TNU":"TransNusa", "ASV":"Air Seoul", "OVA":"Air Europa", "BWA":"Caribbean", "AVL":"Adventures", 
    "THU":"Thunder", "FFM":"FIREFLY", "CGX":"US CG", "CAI":"Corendon", "FFY":"Florida Flyers", "OHC":"Jet Select", "KHV":"Cambodia Air", "APZ":"Air Premia", "SEM":"Cape Central", "RCH":"Air Mobility", 
    "PSW":"Pskov State", "CJX":"Jiangxi", "RSC":"Canarias", "APG":"AirAsia", "DNC":"Aerodynamics", "EPI":"Epic", "DHA":"DHL", "DHX":"DHL", "UBG":"Bangla", "DEV":"Red Devils", "GBX":"Gb Airlink", 
    "JAP":"JetSMART", "VAG":"Vietravel", "MAX":"Max", "IWY":"interCaribbean", "MBU":"Marabu", "SMR":"Aircompany", "GBG":"GullivAir", "NJM":"Northern Jet", "TMN":"Tasman", "GRL":"Air Greenland", "FMY":"Legere", 
    "CNA":"Canavia Lineas", "GCL":"CargoLogic", "JEC":"JetSMART", "BHS":"Bahamasair", "CGO":"Chicago Air", "CFC":"Canadian AF", "KLC":"KLM", "CEY":"Air Century", "NCA":"Nippon", "APK":"Air Peace", 
    "DQA":"Maldivian", "WIS":"PACC Air", "ABS":"Afrijet", "PHV":"Phenix", "DMD":"RST", "MDA":"Mandarin", "PIC":"Pacific", "SPS":"SPASA", "CVR":"Chevron", "CFS":"Empire", "NCR":"National", "GTA":"GT", 
    "VKG":"Sunclass", "OKC":"Private Jets", "TFX":"Team Global", "AVR":"Avianca", "TCN":"BellAir", "ABD":"Icelandic", "WIF":"Wideroes", "GAF":"German AF", "TUA":"Turkmenistan", "NIA":"Nile Air", 
    "BNL":"Berniq", "TAX":"AirAsia", "ABR":"ASL Ireland", "CWA":"CanWestAir", "REU":"Air Austral", "KPO":"Fly Alliance", "SEK":"Star East", "CTN":"Croatia", "FLI":"Atlantic", "PHJ":"Peach Jet", 
    "TYA":"Nordstar", "LBT":"Nouvel Air", "LVL":"LEVEL", "CQN":"Chongqing", "NWK":"Network", "QLK":"QantasLink", "PSN":"Potosina", "FVJ":"ValueJet", "FIE":"Flyone", "GCF":"Aeronor", "EJM":"Executive Jet", 
    "RMY":"Raya", "ISR":"Israir", "MVK":"North Star", "TPA":"Avianca", "VTR":"Air Ostrava", "PRW":"Primeria Air", "BGA":"Airbus Transport", "BLX":"TUIfly Nordic", "RLC":"Real Aero Club", "DKE":"Jubilee", 
    "QXE":"Horizon", "EVE":"Iberojet", "NMA":"Nesma", "TNO":"AeroUnion", "SHU":"Aurora", "VXP":"Avelo", "CFF":"Aerofan", "MGL":"Mongolian", "HRD":"Marshall", "BIO":"Bio", "BCS":"European Air", "BAV":"Bamboo", 
    "OAE":"Omni Air", "TCE":"Trans-Colorado", "COL":"SC", "DTA":"TAAG Angola", "DAE":"DHL", "SPP":"Sapphire", "ABQ":"Airblue", "JFA":"Jetfly", "PRA":"Flyair", "PAG":"Perimeter", "PRS":"Pars Air", 
    "AIZ":"Arkia Israel", "PRE":"Precision", "OMB":"Omni-Blu", "OAL":"Olympic Air", "GST":"Global SuperTanker", "SPG":"Springdale Air", "MAB":"Airborne LiDAR", "VCJ":"Avcon Jet", "SNG":"LJ Air", 
    "DCS":"Daimler Chrysler", "TAN":"ZanAir", "BMA":"BermudAir", "GZP":"Gazpromavia", "DWC":"Empire San Marino", "GJB":"TransAir", "STL":"Stapleford", "CFA":"Flying Dragon", "IGT":"Georgian", "DCM":"FltPlan", 
    "NYT":"Yeti", "RSD":"Rossiya", "WIT":"Wittering", "VTE":"Contour", "SSF":"Severstal Air", "SZN":"Air Senegal", "QUE":"Service Aerien", "TCS":"Aeronauticos", "VAA":"Van Air", "QAJ":"Quick Air V", 
    "SPH":"Portuguesa", "GDC":"Grand China Air", "GTR":"Galistair", "KAR":"Pegas Fly", "KOW":"Baker", "LER":"Laser", "NYX":"NyxAir", "SRN":"SprintAir", "SVF":"Swedish AF", "IFG":"Infinity", 
    "HKC":"Hong Kong Air", "CMB":"US Transportation", "RBG":"Air Arabia Egypt", "CGD":"Charlotte NG", "GAT":"Gulf Air", "LBQ":"Quest Diagnostics", "CHG":"Challenge", "RFD":"Rafilher", "PDU":"Purdue", 
    "FGN":"Gendarmerie", "MWI":"Malawian", "TGO":"Transport Canada", "FFC":"Fairoaks", "RBA":"Royal Brunei", "UBA":"Myanmar", "CSI":"CSI", "SUT":"Summit Air", "FFL":"ForeFlight", "LAE":"LATAM", 
    "BFY":"Bestfly", "ICT":"Intercontinental", "KSF":"Kent State", "ICN":"Inter Canadian", "PVV":"Fly Pro", "ABB":"Air Belgium", "LYM":"Key Lime Air", "VTB":"Jet Stream", "DEX":"Interflight", 
    "GOS":"Golden Sky", "NTW":"Maxair", "DZR":"Midwest", "RRR":"UK RAF", "DML":"Getjet", "AMQ":"AMC", "ANG":"Air Niugini", "JDL":"JD", "NGL":"Max Air", "AME":"Aeronave Militar", "PTN":"Pantanal Linhas", 
    "NMG":"Genghis Khan", "ESW":"ASG", "SBU":"St Barth", "DNU":"DAT", "DOC":"Norsk", "OEY":"Rimbun Air", "CGF":"Cargo Air", "GSA":"Garden State", "LAO":"Lao", "CFR":"CA Forestry", "UBT":"Norse Atlantic", 
    "TCC":"Trans Continental", "RVP":"Sevenair Air", "BNO":"Babcock", "SYG":"Synergy", "TCV":"TACV", "CNK":"Sunwest", "RZO":"Sata", "AUL":"Smartavia", "MWT":"Midwest", "NHZ":"NHV Helicopters", "PAV":"Proair", 
    "TYW":"TYROL", "VLJ":"La Baule", "ALI":"Airlift", "MMF":"NATO Support", "LJY":"LJ", "AWK":"Airwork", "ALE":"AllianceJet", "FIA":"FlyOne", "SPC":"Skyworld", "THT":"Air Tahiti", "ECN":"Euro Continental", 
    "ADM":"Air Dream College", "GNY":"German Navy", "VAL":"Voyageur", "LET":"Aerolineas", "TVP":"Smartwings", "HGB":"Greater Bay", "TCI":"Amber", "PIP":"Pilot Flyskole", "HAF":"Hellenic AF", "IAM":"Italian AF", 
    "LCO":"LAN", "GAL":"Albatros", "PRF":"Precision Air", "CGR":"Compagnia Generale", "MML":"Hunnu Air", "MNS":"Medsky", "WAF":"Air Flamenco", "TIA":"Trans International", "IAE":"IrAero", "KMK":"Kamaka Air", 
    "GMA":"Gama", "MJF":"Mjet", "RCR":"ROM", "AER":"Alaska Central", "LLN":"Allen", "SDE":"Air Partners", "CWL":"Cranwell", "CNF":"Canaryfly", "FBY":"FlyBy", "ESE":"Avesen", "VOS":"Volaris", "FJO":"Flexjet", 
    "LOG":"Loganair", "WMA":"Makers Air", "AAC":"Army", "CMF":"Air Care", "PUL":"Ornge Air", "SYB":"Sky Service", "NGF":"Air Charity", "NSH":"Gama", "EAX":"Eastern Air", "VRE":"Air Cote D'Ivoire", 
    "SAZ":"Swiss Air-", "MGE":"Asia Pacific", "BTN":"Bhutan", "GOF":"Gof-Air", "HHA":"Atlantic Honduas", "ICV":"Cargolux", "TLK":"Starlink", "RWL":"Rwl", "ROF":"Romanian AF", "ERY":"Sky Quest", 
    "PGA":"Portugalia", "HRT":"Chartright Air", "UNI":"UniCair", "LXA":"Lux", "FGR":"Trans-Pacific Air", "GSP":"Global Flight School", "JTZ":"Nicholas Air", "KEM":"CemAir", "VOC":"Volaris Costa Rica", 
    "GOA":"FLY91", "OUA":"Oklahoma", "REE":"Exclusive", "MAI":"Mauritania", "CGS":"SolitAir", "EIS":"EIS Aircraft", "MAU":"Air Mauritius", "ESF":"Estafeta Aerea", "TCO":"Aerotranscolombiana", "WIA":"Winair", 
    "JTE":"National Jet", "DTR":"Danish Air", "NDU":"North Dakota", "RAN":"Rano Air", "DMN":"Diamond Flight", "HER":"Hera Flight", "GBR":"Rader", "RAP":"Air Center", "CGA":"Congressional Air", "MWG":"MASwings", 
    "VPC":"Panaviatic", "PNC":"Prince", "PSE":"Aeroservicio", "PRZ":"Performance Air", "EOK":"Aero K", "FDR":"Federal Air", "SNC":"Air Cargo", "PRH":"Pro Air", "RNA":"Nepal", "AJK":"Allied Air", 
    "MAA":"Mas Air", "URO":"European", "RON":"Nauru Air", "HUE":"Haute", "BHR":"Bighorn", "HCC":"Heli", "BVR":"Acm Air", "ANO":"Airnorth", "CAV":"Calm Air", "CYT":"Crystal Air", "JKY":"Helicopter", 
    "CFD":"Cranfield", "FRF":"Fleet Air", "RFR":"RAF", "SEN":"Senor Air", "ICC":"Cartografico", "XAM":"Amr", "BNI":"Bartolini", "PSK":"Prescott", "USA":"Silkavia", "MAF":"Aerolineas Mas", "ATX":"AirSwift", 
    "OYO":"Oyonnair", "SRA":"Saudi Royal", "SXT":"Taxi Aereo", "SJI":"Smart Jet", "MLM":"Comlux Malta", "TVR":"TerraAvia", "PHC":"Petroleum", "SDR":"Sundair", "DFC":"Aeropartner", "STB":"Saint Barth", 
    "BGH":"BH Air", "PRN":"Petronord Air", "GEE":"Geeseair", "LAA":"Libyan", "AEZ":"Aeroitalia", "CMA":"CMA CGM", "JAV":"Jordan", "CME":"Prince Edward Air", "XSR":"Airshare", "LHA":"Longhao", 
    "MDF":"Swiftair Hellas", "PJS":"Jet", "SPW":"Speedwings", "LSI":"Aliscargo", "CEL":"Ceiba", "DFA":"Aero Coach", "NWC":"Aircompany NW", "SWT":"Swiftair", "IBX":"Ibex", "FIH":"FinnHEMS", "PRU":"Prinair", 
    "AVJ":"Avia Traffic", "UAG":"Union", "DAF":"Danish AF", "RXI":"Riyadh Air", "HIM":"Himalaya", "TQQ":"Tarco", "FKH":"Fly Khiva", "MGA":"M G Aviacion", "SWU":"SkyAlps", "RER":"Aereoregional", 
    "MJN":"RAF Of Oman", "PWC":"Pratt And Whitney", "AIR":"Airlift", "VET":"Venture", "HMF":"Norrlandsflyg", "PNO":"Panorama Fixed Wings", "QFF":"FlyAden", "SPO":"Aeroservicios", "UCG":"Uniworld Air", 
    "TRF":"Thrust Flight", "CRO":"Crown", "MAV":"Manta Air", "TOG":"CSM", "DXT":"Air Management", "KFS":"Kalitta", "VJA":"Vista America", "CYP":"Cyprus", "MDT":"Sundt Air", "FRA":"Fr", "SRD":"UK Coastguard", 
    "KST":"PTL", "DHL":"Astar Air", "BOO":"BookaJet", "SCO":"Air Charter", "CTL":"Central Air", "TSU":"Gulf", "MGY":"Madagascar", "ROJ":"Royal Jet", "DCW":"DC", "DIC":"Aeromedica", "SVI":"Sky Vision", 
    "SVW":"Silver Arrows", "THS":"Transportes Aereos", "GPM":"Grup Air-Med", "GMD":"Guruge", "NAY":"Naysa", "HGO":"One Air", "LAS":"Skymedia", "QNT":"Qanot Sharq", "GKS":"Hans", "LYC":"Lynden Air", "GDG":"SP", 
    "LLR":"Alliance Air", "NHC":"Northern Helicopter", "CST":"Shoreline", "OOT":"Out of the Blue Air", "RKJ":"Charter", "CAY":"Cayman", "EMD":"Eaglemed", "PTM":"Southeastern", "HFA":"Air Haifa", 
    "AHK":"Air Hong Kong", "OKJ":"Okada", "EXV":"FitsAir", "REB":"Rebus", "MST":"Aeroamistad", "WFL":"W2FLY", "GAS":"Galena Air", "BMJ":"Bemidji", "PJZ":"Premium Jet", "TGY":"Trans Guyana", "PFZ":"Proflight", 
    "EJO":"Execujet", "CBM":"Cherokee", "QAI":"Conquest Air", "HAE":"Kenmore", "PTY":"Petty Transport", "AYR":"British Aerospace", "IBJ":"Air Taxi", "MED":"Ontario", "BOV":"Boliviana", "HAI":"Hai Au", 
    "ABA":"Artem-Avia", "WGN":"Western Global", "CEF":"Czech AF", "UZS":"Air Samarkand", "TDR":"Trade Air", "SPI":"South Pacific", "MAR":"Air Mediterranean", "HBC":"Haitian", "REH":"REACH Air", 
    "MGH":"Mavi Gok", "SRU":"Star Peru", "EPS":"Epps Air", "EXD":"Execujet", "PRI":"Primera Air", "HEZ":"Arrow", "FDO":"France Douanes", "WWP":"Wingo", "LMU":"AlMasria", "TCB":"Transport DelCaribe", 
    "BPC":"Braspress Air", "IML":"Island Air", "GFA":"Gulf Air", "BTQ":"Boutique Air", "CEV":"Centre D'essais", "CFH":"Care Flight", "TCM":"Teledyne", "PWR":"Quanta", "ADB":"Antonov", "UTY":"Alliance", 
    "OVD":"State ATM", "STW":"Southwind", "GLT":"Aero Charter", "EZR":"EZAir", "MNE":"Air Montenegro", "OMT":"CM", "MDO":"Mel Air", "UGD":"Uganda", "ABP":"ABS Jets", "TGU":"TAG", "UAM":"RAF", 
    "IAR":"Iliamna Air", "PCH":"Pilatus", "AFB":"American Falcon", "IRL":"Irish Air Corps", "MMD":"Air Alsie", "PTS":"Points Of Call", "VTA":"Air Tahiti", "NAT":"North Atlantic Air", "TRP":"Maryland Police", 
    "FTO":"Tropic Ocean", "NOJ":"NovaJet", "DBP":"CAA", "CRL":"Corsair", "DON":"Donair", "JUS":"USA Jet", "NDL":"Chrono", "AWA":"Air Astra", "ACL":"AerCaribe", "SLM":"Surinaamse", "PPS":"Butte", 
    "OFT":"Buffalo River", "MPH":"Martinair", "AUR":"Aurigny Air", "CFV":"Calafia", "GHL":"Gatwick", "JDI":"Jet Story", "MJC":"Majestic Air", "FBX":"Flying Business", "PGC":"European", "GES":"Gestair", 
    "PRG":"Empresa", "HVY":"SkyBus Air", "TAY":"ASL", "IYE":"Yemenia", "XGO":"Airgo", "PTA":"Parata Air", "HYP":"Hyperion", "HAS":"Hamburg", "RXA":"Regional", "XAV":"Aviaprom", "RAC":"Icar Air", 
    "CGE":"Nelson College", "HYS":"HiSky Europe", "GRV":"Epsilon", "BOG":"Live Oak Banking", "AUV":"Asia Union", "SEY":"Air Seychelles", "CHR":"Chairman Airmotive", "UCM":"Central Missouri", "SWE":"Svenskt", 
    "SIV":"Slovenian AF", "CYG":"Yana", "TEU":"TAG", "LZB":"Bulgaria Air", "IFC":"Indian AF", "BVN":"Baron", "JON":"Jonair", "FGG":"flyGlobal", "TLR":"Air Libya", "VLZ":"Volare", "CWN":"Crown", 
    "NUA":"United Nigeria", "HTT":"Latitude", "DTH":"Tassili", "AWH":"Aerowest", "EDL":"Bavarian Police", "GHP":"Colvin", "TTN":"Lip-Avia", "GLR":"Central Mountain", "BEZ":"Kingfisher Air", 
    "CYZ":"China Postal", "DGT":"Digital Equipment", "GRD":"National Grid", "LTG":"LATAM", "GBF":"Global", "SWN":"West Air Sweden", "LCT":"TAR Aerolineas", "PIK":"Polizei", "FGC":"Cataluna", "PTL":"Providence", 
    "LXC":"CAE", "STA":"Star", "PHL":"Phillips", "FYG":"Flying Service", "FAF":"Force Aerienne", "GCC":"General Electric", "CEE":"C-Air", "SAE":"Tamara", "IPT":"Interport", "DST":"Aex Air", 
    "ITE":"Interestatal", "ECA":"Excellent Air", "MXA":"Mexicana", "DMR":"Helidosa", "AOM":"Aom-Minerve", "ANK":"Aero Nomad", "GAG":"GreyBird", "CGG":"Walmart", "TAG":"Tag", "SRP":"Polizei", 
    "ETP":"Empire", "FAH":"ASL", "CCP":"Grand Holdings", "BGF":"28th Air Detachment", "IGA":"Skytaxi", "RJC":"Richmor", "PPA":"Propheter", "TJT":"Twin Jet", "CVK":"CAVOK Air", "PPU":"Polish Air", 
    "OXF":"Oxford", "EDG":"Jet Edge", "UAO":"Oxford", "HPJ":"Hop-a-Jet", "ECL":"Euro City Line", "MDS":"Mcneely", "JSD":"BJ", "FGD":"Conair", "GCK":"Glock", "KME":"Cambodia", "MMZ":"Euroatlantic", 
    "NRL":"Nolinor", "AAE":"Air Atlanta", "LYD":"Lyddair", "MAT":"Maine", "BRE":"Air Bretagne", "XEN":"Zenflight", "LPR":"Air Rescue", "VAW":"Fly2Sky", "DEC":"Deltacraft", "RDF":"Eurocopter",
    "LIF":"Rocky Mountain", "CFI":"Flight Inspection", "GMR":"Golden Myanmar", "JDE":"PT Express", "GBJ":"WM Aero Charter", "KSU":"Kansas State", "UAF":"UAE AF", "DIA":"Direct Air", "TEZ":"TezJet", 
    "RQT":"AirQuest", "MAL":"Morningstar Air", "PHD":"Duncan", "LAP":"LATAM Paraguay", "CRE":"Jet OUT", "DVR":"Divi Divi Air", "GKA":"US Army", "GLG":"Avianca Ecuador", "IAN":"Ibom Air", "DMC":"Aerodinamica", 
    "VIP":"Europe Elite", "BSC":"Aerostan", "BFK":"Inner Mongolia", "EFD":"Eisele Flugdienst", "MVP":"Premier Private Jets", "ELG":"Elangeni Gmbh", "ACI":"Air Caledonie", "ARU":"Aruba", "TCK":"Trans Caravan", 
    "CND":"Corendon Dutch", "JMS":"Arc en ciel", "DTL":"Aero Dili", "SHH":"Sky High", "SID":"Sideral Air", "JOC":"Dan Air", "GPX":"GP", "GUM":"Gum Air", "BAY":"Bravo", "GWA":"Great Western Air", 
    "FLZ":"Flightlink", "BEC":"Berkut Air", "PRD":"Presidential Air", "BRQ":"Buraq Air", "RJB":"Panellenic", "SUA":"Eastern Metro", "BBB":"Blackbird Air", "WST":"Western Air", "CHI":"Cougar", "CBR":"Cobra", 
    "IFJ":"IFA", "FCE":"Flight Choice", "GDB":"Gendarmerie", "SFS":"Swiss", "PHN":"Phoenix", "LOL":"Easycharter", "HBT":"Polize", "SWV":"Svensk", "AZQ":"Silk Way", "JLG":"Jet Logistics", 
    "GLF":"Gulfstream Aerospace", "LDG":"Leading Edge", "GGT":"Trans Island", "BBQ":"Eastern Air", "KMI":"K-Mile Air", "SSJ":"KrasAvia", "FSM":"Airpilot", "GAX":"Grand Aire", "GJT":"GetJet", "KAC":"Kuwait", 
    "GDK":"Goldeck-Flug", "POF":"Border Police", "FEL":"Fly Exec", "LRQ":"Luxembourg Air", "TUG":"Turkmenistan", "GUG":"Aviateca", "CXI":"Corendon", "DAI":"Dena", "KGN":"Asman", "MBK":"Chrono Jet", 
    "MTE":"MT Fly", "PBR":"Fast Air", "LDX":"Sparfell", "GXA":"GlobalX", "KBA":"Kenn Borek", "PVD":"PAD", "CSW":"Chair", "CSA":"Czech", "SPZ":"Airworld", "LYF":"Lithuanian AF", "QAZ":"Qazaq Air", 
    "PNY":"Polish Navy", "TGZ":"Georgian", "RGA":"Swiss Air", "FAC":"Colombian AF", "AXY":"Air X Charter", "JSX":"JSX", "ASY":"Australian RAF", "SRR":"Maersk Air", "GLX":"Gelix", "EUK":"Aer Lingus", 
    "MYU":"My Indo", "AOS":"Servicios Aereos", "SEL":"Sentel", "PKP":"Mountain Air", "PLF":"Polish AF", "AAB":"Abelag", "PAC":"Polar Air", "MSU":"Maluti Sky", "AGH":"Altagna", "DOW":"Best Jets", 
    "KEW":"Keewatin Air", "EUP":"Euroair", "CAR":"Inter Rca", "UKL":"Airalliance", "RTY":"Aims College", "KXP":"MJets Air", "BRI":"Air Bor", "SCU":"Spartan College", "BNJ":"Air Service Liege", "SKK":"ASKY", 
    "GJE":"Global Jet", "JTL":"Jet Linx", "SIY":"Executive", "TOY":"Toyo", "SIL":"Silver", "CIR":"Arctic Circle", "KNM":"Air Enterprise", "GCT":"GC", "LXR":"Sky Prime", "ADV":"Advance Air", 
    "SCQ":"OSM Academy", "NCJ":"North Central", "LXP":"LAN", "OOM":"Zoom", "ICL":"CAL", "SAT":"SATA Air", "EAL":"Eastern", "EAU":"Elitavia"
}

# Global Vars
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_VRADARSERVER_AIRLINE = "./data/vradarserver-airline.db"

# Init logger
logger = logging.getLogger("flight_tracks")


def get_airline(callsign) -> str:
    '''
    Lookup airline based on callsign using embedded airline_dict
    If not found, then try vradarserver database (vradarserver_airline.db)
    '''

    desc = "n/a"
    logger.debug("get_airline: callsign: %s", callsign)
    if not callsign or len(callsign) < 3:
        return desc

    # Lookup airline within airline_dict
    try:
        desc = airline_dict[callsign[:3]]
        logger.debug("get_airline: Dictionary result: %s", desc)
    except KeyError:
        logger.debug("get_airline: Dictionary result: n/a")

    if desc == "n/a":
        # Connect to DB_VRADARSERVER_AIRLINE
        conn = sqlite3.connect(SCRIPT_DIR / DB_VRADARSERVER_AIRLINE)
        cursor = conn.cursor()

        cursor.execute("SELECT Name FROM airline WHERE Code = ?", (callsign[:3],))
        row = cursor.fetchone()
        if row:
            desc = row[0]
            logger.debug("get_airline: Database result: %s", desc)
        else:
            logger.debug("get_airline: Database result: n/a")
        conn.close()
    return desc
