import pyodbc

# Define ODBC connection parameters
prod_connection_params = {
    'dsn_name': 'tl_prod',
    'user': 'dba',
    'password': 'khm08',
    'database_name': 'tl_prod',
    'server_name': 'dbserv'
}

# Establish connection to Prod database
prod_connection = pyodbc.connect(
    'DSN={};UID={};PWD={};DATABASE={};SERVER={}'.format(
        prod_connection_params['dsn_name'],
        prod_connection_params['user'],
        prod_connection_params['password'],
        prod_connection_params['database_name'],
        prod_connection_params['server_name']
    )
)

# Create cursor
prod_cursor = prod_connection.cursor()

# Execute a query
#prod_cursor.execute("SELECT * FROM your_table")

# Define date range parameters
start_date = '2024-01-01'
end_date = '2024-12-31'

# Execute the SELECT query with date parameters
prod_cursor.execute("""
                    SELECT 
                    bel.nr as "BelNr",
                    bel.datum as "BelDatum",
                    bel.adr1name1 as "BelAdr1Name1",
                    bel.adr1name2 as "BelAdr1Name2",
                    bel.adr1name3 as "BelAdr1Name3", 
                    bel.adr1zeile1 as "BelAdr1Zeile1",
                    bel.adr1zeile2 as "BelAdr1Zeile2",
                    bel.adr1zeile3 as "BelAdr1Zeile3", 
                    bel.adr1plz as "Adr1Plz",
                    bel.adr1ort as "Adr1Ort",
                    bel.adr1land as "Adr1Land",
                    bel.waehrg_menge as "WaehrgMenge",
                    bel.summenetto as "Summenetto",
                    bel.summebrutto as "Summebrutto",
                    bel.dispo_datum as "BelDispoDatum",
                    bel.dispo_kw as "BelDispoKW",
                    bel.dispo_jahr as "BelDispoJahr",
                    bel.gewichtbrutto as "BelGewichtBrutto",
                    bel.gewichtnetto as "BelGewichtNetto",
                    bel.kunden_ab_nr as "BelKundenAbNr",
                    bel.kunden_ab_datum as "BelKundenAbDatum",
                    bel.erstellt_am as "BelErstelltAm",
                    bel.erstellt_von as "BelErstelltVon",
                    belpos.artikelek as "Artikelek",
                    belpos.ek_lager as "EkLager",
                    belpos.dispo_datum as "PosDispoDatum",
                    belpos.gewicht as "PosGewicht",
                    belpos.gew_einheit as "PosGewEinheit",
                    belpos.provision as "Provision",
                    belpos.preiseinh as "Preiseinh",
                    belpos.verpeinh as "Verpeinh",
                    belpos.einzel_basis as "EinzelBasis",
                    belpos.rabatt1 as "Rabatt1",
                    belpos.mahnstufe as "Mahnstufe",
                    belpos.mahndatum as "Mahndatum",
                    belpos.mtz_umstellgruppe as "MtzUmstellGruppe",
                    belpos.verpackg_id as "VerpackgID",
                    belpos.orig_menge as "OrigMenge",
                    belpos.vorgangs_nr as "VorgangsNr",
                    belpos.kd_wunschtermin as "KdWunschtermin",
                    belpos.projekt_id as "ProjektID",
                    belpos.zeich_nr as "ZeichNr",
                    belpos.sendg_nr as "SendgNr",
                    belpos.sendg_beltyp as "SendgBelTyp",
                    belpos.sendg_belnr as "SendgBelNr",
                    belpos.sendg_posnr as "SendgPosNr",
                    belpos.posnr as "PosNr", belpos.art_nr as "ArtNr", belpos.bez1 as "Bezeichnung", belpos.menge as "Menge", belpos.uebernommen as "Übernommen", belpos.mm_laufzettel_uebern as "Laufzettel Übern.", belpos.rabattpro as "RabattPro",belpos.einzelpr as "Einzelpreis", belpos.komm_nr as "Kd-KommNr", 
                    belpos.mm_index as "Index", belpos.ind_string_01 as "AuftragNr", LEFT(belpos.kunden_ab_nr, LOCATE(belpos.kunden_ab_nr, '/') - 1) as "KD-BelNr", belpos.kunden_ab_datum as "KD-BelDatum", belpos.zendpreis as "Endpreis", ((IF cast((belpos.dispo_kw / 10) as int) = 0 THEN 'KW0' ELSE 'KW' ENDIF) + string(belpos.dispo_kw)) as "DispoKw", belpos.dispo_jahr as "DispoJahr", bel.pers_nr as "KD-Nr", (coalesce(bel.adr1name1, '') + '  ' + coalesce(bel.adr1name2, '') ) as "KD-Name",
                    (SELECT art.artgrp FROM art WHERE art.artnr = belpos.art_nr) AS "ArtGruppe",
                    (SELECT artgrp.bez FROM artgrp WHERE artgrp.nr = ArtGruppe) AS "ArtGrpBez",
                    (SELECT artgrp.mm_tarifnr FROM artgrp WHERE artgrp.nr = ArtGruppe) AS "MMTarif",
                    ( IF (SELECT art.ind_long_01 FROM art WHERE art.artnr = belpos.art_nr) = 1 THEN 'Ja' ELSE 'Nein' ENDIF)  AS "MOR",
                    (SELECT mm_lackierg.bez FROM mm_lackierg WHERE mm_lackierg.nr =  (SELECT art.ind_long_02 FROM art WHERE art.artnr = belpos.art_nr)) AS "Lackierung",
                    (SELECT zk.bez1 FROM zk WHERE zk.nr = bel.zk_nr) AS "Zahlung",
                    (SELECT persgrp.bez FROM persgrp WHERE persgrp.nr = (SELECT pers.persgruppe FROM pers WHERE pers.typ = bel.pers_typ AND pers.nr = bel.pers_nr )) AS "PersGruppe",
                    (SELECT art.bez2 FROM art WHERE art.artnr = belpos.art_nr) AS "Bez2" , belpos.ind_string_01 as "Kundenkomm.nr"
                    FROM belpos, bel  
                    WHERE  (belpos.bel_typ = 4) AND bel.typ = belpos.bel_typ AND bel.nr = belpos.bel_nr AND date(bel.datum) >=? AND date(bel.datum)  <= ? 
                    ORDER BY bel.nr ASC
""", start_date, end_date)
columns = [column[0] for column in prod_cursor.description]
print(columns)

# Fetch one row
#row = prod_cursor.fetchone()
#print(row)

# Fetch all remaining rows

rows = prod_cursor.fetchall()

for row in rows:
    print(';'.join(map(str, row)))

# Close cursor and connection
prod_cursor.close()
prod_connection.close()
