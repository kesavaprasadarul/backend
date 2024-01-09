"""Add association tables for vorgang

Revision ID: 7579d89290ea
Revises: 038e6a9eee2b
Create Date: 2023-12-18 11:58:14.042682

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7579d89290ea'
down_revision: Union[str, None] = '038e6a9eee2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        'vorgang',
        'drucksache_id',
        schema='dip',
    )

    op.drop_column(
        'vorgang',
        'plenarprotokoll_id',
        schema='dip',
    )

    op.create_table(
        'plenarprotokoll_vorgang_association',
        sa.Column('plenarprotokoll_id', sa.Integer(), nullable=False),
        sa.Column('vorgang_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['plenarprotokoll_id'],
            ['dip.plenarprotokoll.id'],
        ),
        sa.ForeignKeyConstraint(
            ['vorgang_id'],
            ['dip.vorgang.id'],
        ),
        schema='dip',
    )

    op.create_table(
        'drucksache_vorgang_association',
        sa.Column('drucksache_id', sa.Integer(), nullable=False),
        sa.Column('vorgang_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['drucksache_id'],
            ['dip.drucksache.id'],
        ),
        sa.ForeignKeyConstraint(
            ['vorgang_id'],
            ['dip.vorgang.id'],
        ),
        schema='dip',
    )

    op.execute(
        r"""
        DROP FUNCTION count_weekly_drucksache(DATE, DATE, TEXT[], TEXT[]);
        """
    )

    op.execute(
        r"""
        CREATE FUNCTION count_weekly_drucksache(
                        in_date_from DATE,
                        in_date_to DATE,
                        drucksachetyp_filter TEXT[],
                        vorgangstyp_filter TEXT[]
                )
        RETURNS TABLE (
            "year"				INT,
            "week"				INT,
            week_start_date 	DATE,
            week_end_date 		DATE,
            drucksache_count 	BIGINT
        )
        LANGUAGE plpgsql
        AS 
        $func$
        BEGIN
                
            DROP TABLE IF EXISTS temp_params;
            CREATE TEMPORARY TABLE temp_params AS 
            SELECT in_date_from 		AS date_from
                , in_date_to 	 		AS date_to
                , drucksachetyp_filter
                , vorgangstyp_filter;
            
            -- Debug
        	/*
                DROP TABLE IF EXISTS temp_params;
                CREATE TEMPORARY TABLE temp_params AS 
                SELECT '2023-12-01'::DATE  AS date_from
                    , (NOW() + interval '1 week')::DATE AS date_to
                    , '{
                            "Beschluss",
                            "Gesetzgebung",
                            "Beschlussempfehlung und Bericht",
                            "Empfehlungen"
                        }'::TEXT[] AS drucksachetyp_filter
                    , '{	
                            "Antrag",
                            "Entschließungsantrag BT", 
                            "Gesetzgebung",
                            "Rechtsverordnung", 
                            "Untersuchungsausschuss",
                            "Wahl im BT"
                        }'::TEXT[] AS vorgangstyp_filter;
            -- */
            
            DROP TABLE IF EXISTS temp_weeks;

            CREATE TEMPORARY TABLE temp_weeks AS 
            select extract(isoyear from t.week_day)::int as year
                , extract(week from t.week_day)::int as nr
                , date_trunc('week', t.week_day)::DATE as week_start
                , (date_trunc('week', t.week_day) + interval '6 days')::DATE as week_end
            from generate_series((SELECT tp.date_from FROM temp_params tp), 
                                (SELECT tp.date_to FROM temp_params tp),
                                interval '1 week') as t(week_day);
                            
            RETURN QUERY
            WITH drucksache_per_week AS (
                SELECT extract(isoyear from D.DATUM) AS year,
                    extract(week from D.DATUM) AS nr, 
                    COUNT(DISTINCT D.ID) drucksache_count
                FROM temp_params tp, dip.DRUCKSACHE D 
                LEFT JOIN dip.DRUCKSACHE_VORGANG_ASSOCIATION DVA ON D.ID = DVA.drucksache_id
                JOIN dip.VORGANG V ON DVA.vorgang_id = V.ID
                WHERE CASE WHEN tp.vorgangstyp_filter IS NOT NULL THEN V.vorgangstyp =  ANY (tp.vorgangstyp_filter)
                        ELSE TRUE 
                        END
                AND CASE WHEN tp.drucksachetyp_filter IS NOT NULL THEN D.drucksachetyp = ANY(tp.drucksachetyp_filter)
                        ELSE TRUE 
                        END
                GROUP BY extract(week from D.DATUM), extract(isoyear from D.DATUM )
                
            ) 
            SELECT w.year AS "year"
                , w.nr AS "week"
                , w.week_start AS week_start_date
                , w.week_end AS week_end_date
                , COALESCE(dpw.drucksache_count, 0) as drucksache_count
            FROM temp_weeks w
            LEFT JOIN drucksache_per_week dpw ON w.year = dpw.year AND w.nr = dpw.nr;

        END;
        $func$;
	"""
    )

    op.execute(
        r"""
		DROP PROCEDURE import_abstimmungen(TEXT[], TEXT[]);
      	"""
    )

    op.execute(
        r"""
		CREATE PROCEDURE import_abstimmungen(
            drucksachetyp_filter TEXT[],
            vorgangstyp_filter TEXT[]
        )
        LANGUAGE plpgsql
        AS 
        $func$
        BEGIN
            DROP TABLE IF EXISTS temp_params;
            CREATE TEMPORARY TABLE temp_params AS 
            SELECT drucksachetyp_filter
                , vorgangstyp_filter;
            
            -- Debug
                /*
                DROP TABLE IF EXISTS temp_params;
                CREATE TEMPORARY TABLE temp_params AS 
                SELECT '{
                            "Beschluss",
                            "Gesetzgebung",
                            "Beschlussempfehlung und Bericht",
                            "Empfehlungen"
                        }'::TEXT[] AS drucksachetyp_filter
                    , '{	
                            "Antrag",
                            "Entschließungsantrag BT", 
                            "Gesetzgebung",
                            "Rechtsverordnung", 
                            "Untersuchungsausschuss",
                            "Wahl im BT"
                        }'::TEXT[] AS vorgangstyp_filter;
            -- */
                    
                    
            DROP TABLE IF EXISTS temp_new_abstimmungen;
            CREATE TEMPORARY TABLE temp_new_abstimmungen AS 
            WITH new_abstimmungen AS (	
                SELECT VP.id AS dip_vorgangsposition_id
                    , V.titel
                    , V.abstract
                    , V.sachgebiet
                    , VP.datum AS abstimmung_datum
                    , B.abstimmungsart
                    -- , V.vorgangstyp
                    -- , VP.datum
                    , VP.aktualisiert
                    , V.initiative
                    , B.id AS beschlussfassung_id
                    , B.beschlusstenor
                    , B.abstimm_ergebnis_bemerkung
                    , M.anzahl_stimmberechtigt 
                FROM temp_params tp, dip.DRUCKSACHE D
                JOIN dip.DRUCKSACHE_VORGANG_ASSOCIATION DVA ON D.ID = DVA.DRUCKSACHE_ID
                JOIN dip.VORGANG V ON DVA.VORGANG_ID = V.ID
                JOIN dip.VORGANGSPOSITION VP ON V.ID = VP.VORGANG_ID 
                JOIN dip.BESCHLUSSFASSUNG B ON VP.ID = B.VORGANGSPOSITION_ID 
                JOIN public.mandate M ON M.DATE_FROM <= D.DATUM AND (M.DATE_TO IS NULL OR M.DATE_TO >= D.datum)
                LEFT JOIN public.ABSTIMMUNG A ON VP.id = A.dip_vorgangsposition_id
                AND (M.DATE_TO IS NULL OR M.DATE_TO >= VP.DATUM)
                WHERE VP."zuordnung" = 'BT'
                AND V.vorgangstyp =  ANY (tp.vorgangstyp_filter)
                AND D.drucksachetyp = ANY(tp.drucksachetyp_filter)
                AND ABSTIMM_ERGEBNIS_BEMERKUNG IS NOT NULL
                AND ABSTIMM_ERGEBNIS_BEMERKUNG ~* '\d+:\d+:\d+\s?.*' 
                AND (A.id IS NULL OR (A.id IS NOT NULL AND A.aktualisiert <= VP.aktualisiert)
                                    OR (A.aktualisiert IS NULL AND VP.aktualisiert IS NOT NULL))
            ) 
            SELECT titel
                , abstract
                , sachgebiet
                , abstimmung_datum
                , abstimmungsart
                , CASE 
                    WHEN beschlusstenor ILIKE '%annahme%' THEN TRUE 
                    ELSE FALSE
                    END AS akzeptiert
                , split_part(abstimm_ergebnis_bemerkung, ':', 1)::INT AS "ja"
                , split_part(abstimm_ergebnis_bemerkung, ':', 2)::INT AS "nein"
                , substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\d+')::INT AS "enthalten"
                , anzahl_stimmberechtigt
                    - split_part(abstimm_ergebnis_bemerkung, ':', 1)::INT
                    - split_part(abstimm_ergebnis_bemerkung, ':', 2)::INT
                    - substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\d+')::INT AS "nicht_abgegeben"
                , btrim(substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\s?[(](.+)?'), '()') AS "ergebnis_anmerkung"
                , aktualisiert
                , initiative
                , beschlussfassung_id
                , dip_vorgangsposition_id
                , anzahl_stimmberechtigt
            FROM new_abstimmungen;
            
            INSERT INTO public.ABSTIMMUNG (
                titel
                , abstract
                , sachgebiet
                , abstimmung_datum
                , abstimmungsart
                , akzeptiert
                , ja
                , nein
                , enthalten
                , nicht_abgegeben
                , ergebnis_anmerkung
                , aktualisiert
                , initiative
                , beschlussfassung_id
                , dip_vorgangsposition_id
            ) 
            SELECT DISTINCT titel
                , abstract
                , sachgebiet
                , abstimmung_datum
                , abstimmungsart
                , akzeptiert
                , ja
                , nein
                , enthalten
                , nicht_abgegeben
                , ergebnis_anmerkung
                , aktualisiert
                , initiative
                , beschlussfassung_id
                , dip_vorgangsposition_id
            FROM temp_new_abstimmungen
            ON CONFLICT (beschlussfassung_id) DO UPDATE
            SET titel = EXCLUDED.titel,
                abstract = EXCLUDED.abstract,
                sachgebiet = EXCLUDED.sachgebiet,
                abstimmung_datum = EXCLUDED.abstimmung_datum,
                abstimmungsart = EXCLUDED.abstimmungsart,
                akzeptiert = EXCLUDED.akzeptiert,
                ja = EXCLUDED.ja,
                nein = EXCLUDED.nein,
                enthalten = EXCLUDED.enthalten,
                nicht_abgegeben = EXCLUDED.nicht_abgegeben,
                ergebnis_anmerkung = EXCLUDED.ergebnis_anmerkung,
                aktualisiert = EXCLUDED.aktualisiert,
                initiative = EXCLUDED.initiative,
                dip_vorgangsposition_id = EXCLUDED.dip_vorgangsposition_id,
                updated_at = EXCLUDED.updated_at;
            
        END;
        $func$;
        """
    )


def downgrade() -> None:
    op.execute(
        r"""
		DROP PROCEDURE import_abstimmungen(TEXT[], TEXT[]);
      	"""
    )
    op.execute(
        r"""
		CREATE PROCEDURE import_abstimmungen(
			drucksachetyp_filter TEXT[],
			vorgangstyp_filter TEXT[]
		)
		LANGUAGE plpgsql
		AS 
		$func$
		BEGIN
			DROP TABLE IF EXISTS temp_params;
			CREATE TEMPORARY TABLE temp_params AS 
			SELECT drucksachetyp_filter
				, vorgangstyp_filter;
			
			-- Debug
			 /*
				DROP TABLE IF EXISTS temp_params;
				CREATE TEMPORARY TABLE temp_params AS 
				SELECT '{
							"Beschluss",
							"Gesetzgebung",
							"Beschlussempfehlung und Bericht",
							"Empfehlungen"
						}'::TEXT[] AS drucksachetyp_filter
					, '{	
							"Antrag",
							"Entschließungsantrag BT", 
							"Gesetzgebung",
							"Rechtsverordnung", 
							"Untersuchungsausschuss",
							"Wahl im BT"
						}'::TEXT[] AS vorgangstyp_filter;
			-- */
					
					
			DROP TABLE IF EXISTS temp_new_abstimmungen;
			CREATE TEMPORARY TABLE temp_new_abstimmungen AS 
			WITH new_abstimmungen AS (	
				SELECT VP.id AS dip_vorgangsposition_id
					, V.titel
					, V.abstract
					, V.sachgebiet
					, VP.datum AS abstimmung_datum
					, B.abstimmungsart
					-- , V.vorgangstyp
					-- , VP.datum
					, VP.aktualisiert
					, V.initiative
					, B.id AS beschlussfassung_id
					, B.beschlusstenor
					, B.abstimm_ergebnis_bemerkung
					, M.anzahl_stimmberechtigt 
				FROM temp_params tp, dip.DRUCKSACHE D
				JOIN dip.VORGANG V ON D.ID = V.DRUCKSACHE_ID 
				JOIN dip.VORGANGSPOSITION VP ON V.ID = VP.VORGANG_ID 
				JOIN dip.BESCHLUSSFASSUNG B ON VP.ID = B.VORGANGSPOSITION_ID 
				JOIN public.mandate M ON M.DATE_FROM <= D.DATUM AND (M.DATE_TO IS NULL OR M.DATE_TO >= D.datum)
				LEFT JOIN public.ABSTIMMUNG A ON VP.id = A.dip_vorgangsposition_id
				AND (M.DATE_TO IS NULL OR M.DATE_TO >= VP.DATUM)
				WHERE VP."zuordnung" = 'BT'
				AND V.vorgangstyp =  ANY (tp.vorgangstyp_filter)
				AND D.drucksachetyp = ANY(tp.drucksachetyp_filter)
				AND ABSTIMM_ERGEBNIS_BEMERKUNG IS NOT NULL
				AND ABSTIMM_ERGEBNIS_BEMERKUNG ~* '\d+:\d+:\d+\s?.*' 
                AND NOT ABSTIMM_ERGEBNIS_BEMERKUNG ILIKE '%Feststellung der Beschlussfähigkeit%'
				AND (A.id IS NULL OR (A.id IS NOT NULL AND A.aktualisiert <= VP.aktualisiert)
									OR (A.aktualisiert IS NULL AND VP.aktualisiert IS NOT NULL))
			) 
			SELECT titel
				, abstract
				, sachgebiet
				, abstimmung_datum
				, abstimmungsart
				, CASE 
					WHEN beschlusstenor ILIKE '%annahme%' THEN TRUE 
					ELSE FALSE
					END AS akzeptiert
				, split_part(abstimm_ergebnis_bemerkung, ':', 1)::INT AS "ja"
				, split_part(abstimm_ergebnis_bemerkung, ':', 2)::INT AS "nein"
				, substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\d+')::INT AS "enthalten"
				, anzahl_stimmberechtigt
					- split_part(abstimm_ergebnis_bemerkung, ':', 1)::INT
					- split_part(abstimm_ergebnis_bemerkung, ':', 2)::INT
					- substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\d+')::INT AS "nicht_abgegeben"
				, btrim(substring(split_part(abstimm_ergebnis_bemerkung, ':', 3) from '\s?[(](.+)?'), '()') AS "ergebnis_anmerkung"
				, aktualisiert
				, initiative
				, beschlussfassung_id
				, dip_vorgangsposition_id
				, anzahl_stimmberechtigt
			FROM new_abstimmungen;
			
			INSERT INTO public.ABSTIMMUNG (
				titel
				, abstract
				, sachgebiet
				, abstimmung_datum
				, abstimmungsart
				, akzeptiert
				, ja
				, nein
				, enthalten
				, nicht_abgegeben
				, ergebnis_anmerkung
				, aktualisiert
				, initiative
				, beschlussfassung_id
				, dip_vorgangsposition_id
			) 
			SELECT titel
				, abstract
				, sachgebiet
				, abstimmung_datum
				, abstimmungsart
				, akzeptiert
				, ja
				, nein
				, enthalten
				, nicht_abgegeben
				, ergebnis_anmerkung
				, aktualisiert
				, initiative
				, beschlussfassung_id
				, dip_vorgangsposition_id
			FROM temp_new_abstimmungen
			ON CONFLICT (beschlussfassung_id) DO UPDATE
			SET titel = EXCLUDED.titel,
				abstract = EXCLUDED.abstract,
				sachgebiet = EXCLUDED.sachgebiet,
				abstimmung_datum = EXCLUDED.abstimmung_datum,
				abstimmungsart = EXCLUDED.abstimmungsart,
				akzeptiert = EXCLUDED.akzeptiert,
				ja = EXCLUDED.ja,
				nein = EXCLUDED.nein,
				enthalten = EXCLUDED.enthalten,
				nicht_abgegeben = EXCLUDED.nicht_abgegeben,
				ergebnis_anmerkung = EXCLUDED.ergebnis_anmerkung,
				aktualisiert = EXCLUDED.aktualisiert,
				initiative = EXCLUDED.initiative,
				dip_vorgangsposition_id = EXCLUDED.dip_vorgangsposition_id,
				updated_at = EXCLUDED.updated_at;
			
		END;
		$func$;
        """
    )
    op.execute(
        r"""
        DROP FUNCTION count_weekly_drucksache(DATE, DATE, TEXT[], TEXT[]);
        """
    )

    op.execute(
        r"""
		CREATE FUNCTION count_weekly_drucksache(
				in_date_from DATE,
				in_date_to DATE,
				drucksachetyp_filter TEXT[],
				vorgangstyp_filter TEXT[]
		)
		RETURNS TABLE (
			"year"				INT,
			"week"				INT,
			week_start_date 	DATE,
			week_end_date 		DATE,
			drucksache_count 	BIGINT
		)
		LANGUAGE plpgsql
		AS 
		$func$
		BEGIN
				
			DROP TABLE IF EXISTS temp_params;
			CREATE TEMPORARY TABLE temp_params AS 
			SELECT in_date_from 		AS date_from
				, in_date_to 	 		AS date_to
				, drucksachetyp_filter
				, vorgangstyp_filter;
			
			-- Debug
			/*
				DROP TABLE IF EXISTS temp_params;
				CREATE TEMPORARY TABLE temp_params AS 
				SELECT '2023-12-01'::DATE  AS date_from
					, (NOW() + interval '1 week')::DATE AS date_to
					, '{
							"Beschluss",
							"Gesetzgebung",
							"Beschlussempfehlung und Bericht",
							"Empfehlungen"
						}'::TEXT[] AS drucksachetyp_filter
					, '{	
							"Antrag",
							"Entschließungsantrag BT", 
							"Gesetzgebung",
							"Rechtsverordnung", 
							"Untersuchungsausschuss",
							"Wahl im BT"
						}'::TEXT[] AS vorgangstyp_filter;
			-- */
			
			DROP TABLE IF EXISTS temp_weeks;

			CREATE TEMPORARY TABLE temp_weeks AS 
			select extract(isoyear from t.week_day)::int as year
				, extract(week from t.week_day)::int as nr
				, date_trunc('week', t.week_day)::DATE as week_start
				, (date_trunc('week', t.week_day) + interval '6 days')::DATE as week_end
			from generate_series((SELECT tp.date_from FROM temp_params tp), 
								(SELECT tp.date_to FROM temp_params tp),
								interval '1 week') as t(week_day);
							
			RETURN QUERY
			WITH drucksache_per_week AS (
				SELECT extract(isoyear from D.DATUM) AS year,
					extract(week from D.DATUM) AS nr, 
					COUNT(DISTINCT D.ID) drucksache_count
				FROM temp_params tp, dip.DRUCKSACHE D 
				LEFT JOIN dip.VORGANG V ON D.id = V.drucksache_id 
				WHERE V.ID IS NULL OR ( -- Some vorgänge have multiple drucksachen. This would effectively mean we lose count if theyre overriden
				-- We don't really care tho about this => it might affect some data counts but the effect is probably minimal
				-- In the future we should have a mapping table between vorgaenge, plenarprotokolle and drucksachen
				-- This would give us the opportunity to actually guarantee consistency with API data
				CASE WHEN tp.vorgangstyp_filter IS NOT NULL THEN V.vorgangstyp =  ANY (tp.vorgangstyp_filter)
						ELSE TRUE 
						END
				)
				AND CASE WHEN tp.drucksachetyp_filter IS NOT NULL THEN D.drucksachetyp = ANY(tp.drucksachetyp_filter)
						ELSE TRUE 
						END
				GROUP BY extract(week from D.DATUM), extract(isoyear from D.DATUM )
				
			) 
			SELECT w.year AS "year"
				, w.nr AS "week"
				, w.week_start AS week_start_date
				, w.week_end AS week_end_date
				, COALESCE(dpw.drucksache_count, 0) as drucksache_count
			FROM temp_weeks w
			LEFT JOIN drucksache_per_week dpw ON w.year = dpw.year AND w.nr = dpw.nr;

		END;
		$func$;
        """
    )

    op.drop_table('drucksache_vorgang_association', schema='dip')
    op.drop_table('plenarprotokoll_vorgang_association', schema='dip')

    op.add_column(
        'vorgang',
        sa.Column('plenarprotokoll_id', sa.INTEGER(), autoincrement=False, nullable=True),
        schema='dip',
    )

    op.create_foreign_key(
        None,
        'vorgang',
        'plenarprotokoll',
        ['plenarprotokoll_id'],
        ['id'],
        ondelete='CASCADE',
        onupdate='CASCADE',
        source_schema="dip",
        referent_schema="dip",
    )

    op.add_column(
        'vorgang',
        sa.Column('drucksache_id', sa.INTEGER(), autoincrement=False, nullable=True),
        schema='dip',
    )

    op.create_foreign_key(
        None,
        'vorgang',
        'drucksache',
        ['drucksache_id'],
        ['id'],
        ondelete='CASCADE',
        onupdate='CASCADE',
        source_schema="dip",
        referent_schema="dip",
    )
