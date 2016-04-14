import zipfile
import os
from OvlReader.copexreader.COPEx import *
from MultiSymbolConverter import MultiSymbolConverter
from MSSSymbolConverter import MSSSymbolConverter
from MultiSymbolLineConverter import MultiSymbolLineConverter
from COPExObject2MSSConverter import COPExObject2MSSConverter


base_dir = os.path.dirname(os.path.abspath(__file__))

symbol2mss_converter = [
    MultiSymbolConverter(base_dir + '\..\..\mapping'),
    MultiSymbolLineConverter(base_dir + '\..\..\mapping'),
    MSSSymbolConverter()
]

mapping_found = 0
symbol_count = 0


def main():

    mss_symbols_strings = [
        'GZ="Freund";ZZ0="Bat/Abt/Geschw";ZZ1="Pz_Sap";TEXT5="11";TEXT9="5";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="0, 0, 255";SYM_ANGLE="0";LINE_SIZE="2";',
        'GZ="Gegner";ZZ0="Bat/Abt/Geschw";ZZ1="Pz_Sap";TEXT5="10";TEXT8="DRA";TEXT9="4";LANGUAGE="Armee";SYM_SIZE="75";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="3";',
        'GZ="Gegner";ZZ0="Gr";ZZ1="Pz_Sap";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="4";',
        'GZ="Gegner";ZZ0="Kp/Bttr/St/Kol/Det";ZZ1="Pz_Sap";TEXT5="2";TEXT9="10";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="2";',
        'GZ="Gegner";ZZ0="Kp/Bttr/St/Kol/Det";ZZ1="Pz_Sap";TEXT5="3";TEXT9="10";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="2";',
        'GZ="Gegner";ZZ0="Kp/Bttr/St/Kol/Det";ZZ1="Pz_Sap";TEXT5="4";TEXT9="10";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="2";',
        'GZ="Gegner";ZZ0="Rgt/Kdo";TEXT0="SOK";TEXT5="1";TEXT8="DRA";LANGUAGE="Armee";SYM_SIZE="75";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="3";',
        'GZ="Gegner";ZZ0="Rgt/Kdo";ZZ1="Mrakw_F_Art";TEXT5="61";TEXT9="6";LANGUAGE="Armee";SYM_SIZE="90";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="4";',
        'GZ="Gegner";ZZ0="Z";ZZ1="Pz_Gren_Gegner";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="2";',
        'GZ="Gegner";ZZ0="Z";ZZ1="Pz_Gren_Gegner";LANGUAGE="Armee";SYM_SIZE="60";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="255, 0, 0";SYM_ANGLE="0";LINE_SIZE="4";',
        'GZ="Stab";ZZ0="Bat/Abt/Geschw";ZZ1="M_Flab";ZZ3="Mob_Fo";TEXT9="90";LANGUAGE="Armee";SYM_SIZE="75";STATUS="REAL";LINE_PATTERN="SOLID";FILL_PATTERN="HOLLOW";COLOR="0, 0, 255";SYM_ANGLE="0";LINE_SIZE="2";',
        'LINE_SIZE="2";COLOR="255,0,0";FILL_COLOR="255,255,255";FILL_PATTERN="HOLLOW";LINE_PATTERN="SOLID";SYM_SIZE="40";SYM_ANGLE="0";GZ="Sperre";TEXT8="x";LANGUAGE="ZDV1/11";',
        'LINE_SIZE="4";COLOR="255,0,0";FILL_COLOR="255,255,255";FILL_PATTERN="HOLLOW";LINE_PATTERN="SOLID";SYM_SIZE="120";SYM_ANGLE="0";GZ="Gegner";ZZ0="Rgt/Kdo";TEXT0="SOK";TEXT5="1";TEXT8="DRA";LANGUAGE="Armee";'
    ]

    mss_line_symbols_strings = [
        'LINIENART="BASISTYP=\"LINIE_Stellung\";BASISFORM=\"GERADE\";COLOR=\"255, 0, 0\";FILL_COLOR=\"0,0,255\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Panzerinenfeld\";BASISTYP=\"RAUM_Sperre\";COLOR=\"255, 0, 0\";FILL_COLOR=\"0,0,255\";LINE_SIZE=\"1\";LINE_PATTERN=\"SOLID\";BASISFORM=\"GERADE\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"Cgm\";AUSDEHNUNG=\"20\";POSITION=\"-60 DISTANCE\";VERSCHIEBERICHTUNG=\"FEST\";VERSCHIEBEABSTAND=\"0\";WINKELAUSRICHTUNG=\"ANLIEGEND\";OBJEKTTYP=\"CGM\";OBJEKTINHALT=\"GFX_Panzerminenfeld; ;\";CLIPPING=\"FALSE\";ALIGMENT=\"MITTE\";";',
        'LINIENART="KLASSENNAME=\"Panzerinenfeld\";BASISTYP=\"RAUM_Sperre\";COLOR=\"255, 0, 0\";FILL_COLOR=\"0,0,255\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";BASISFORM=\"GERADE\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"Cgm\";AUSDEHNUNG=\"20\";POSITION=\"-60 DISTANCE\";VERSCHIEBERICHTUNG=\"FEST\";VERSCHIEBEABSTAND=\"0\";WINKELAUSRICHTUNG=\"ANLIEGEND\";OBJEKTTYP=\"CGM\";OBJEKTINHALT=\"GFX_Panzerminenfeld; ;\";CLIPPING=\"FALSE\";ALIGMENT=\"MITTE\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 255\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"4\";LINE_PATTERN=\"DOT\";FILL_PATTERN=\"HOLLOW\";STATUS=\"PLAN\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"840\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,255,255\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"840\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 255\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255, 0, 0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"DIAGCROSS\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"4\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffVerstaerkt\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,255,255\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"720\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 255\";FILL_COLOR=\"0,0,255\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"180\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"160\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"200\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"520\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"340\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_Angriff\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"3\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"590\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 0\";FILL_COLOR=\"0, 0, 0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"SOLID\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 255\";FILL_COLOR=\"0, 0, 255\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"SOLID\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"0, 128, 0\";FILL_COLOR=\"0, 128, 0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"SOLID\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffsPfeil\";BASISFORM=\"GERUNDET\";COLOR=\"255, 0, 0\";FILL_COLOR=\"255, 0, 0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"SOLID\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffVerstaerkt\";BASISFORM=\"GERUNDET\";COLOR=\"0, 0, 255\";FILL_COLOR=\"0,0,255\";LINE_SIZE=\"4\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";STATUS=\"REAL\";SYM_ANGLE=\"0\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"220\";";',
        'LINIENART="KLASSENNAME=\"Ttigkeit\";KLASSENARTNAME=\"bek\";BASISTYP=\"PFEIL_AngriffVerstaerkt\";BASISFORM=\"GERUNDET\";COLOR=\"255,0,0\";FILL_COLOR=\"255,0,0\";LINE_SIZE=\"2\";LINE_PATTERN=\"SOLID\";FILL_PATTERN=\"HOLLOW\";";LINIENOBJ0="KOMPONENTENNAME=\"AngriffspfeilBreite\";OBJEKTTYP=\"PARAMETER\";OBJEKTINHALT=\"140\";";'
    ]

    copex_objs = []
    for sym_str in mss_symbols_strings:

        copex_obj = MultiSymbolObject()
        copex_obj.symbol_string = sym_str

        copex_objs.append(copex_obj)

    for sym_str in mss_line_symbols_strings:

        copex_obj = MultiSymbolLineObject()
        copex_obj.symbol_string = sym_str

        copex_objs.append(copex_obj)

    for copex_obj in copex_objs:
        symbol_def = None
        for converter in symbol2mss_converter:
            symbol_def = converter.map(copex_obj)
            if symbol_def is not None:
                break

        if symbol_def is not None:
            # print(symbol_def)
            # print("MSS-Lib XML String: " + COPExObject2MSSConverter.get_mms_string(symbol_def))
            print("OK: " + copex_obj.get_symbol_string() + "\t" + COPExObject2MSSConverter.get_mms_string(symbol_def))
            pass
        else:
            # print("Conversion failed : " + copex_obj.get_symbol_string())
            print("FAILED: " + copex_obj.get_symbol_string())


if __name__ == '__main__':
    main()
