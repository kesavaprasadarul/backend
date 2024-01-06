"""Rename old abstimmungen procedure

Revision ID: e09b444525fc
Revises: 980d5a591c7c
Create Date: 2024-01-06 20:53:45.379704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e09b444525fc'
down_revision: Union[str, None] = '980d5a591c7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        r"""
		DROP PROCEDURE import_abstimmungen(TEXT[], TEXT[]);
      	"""
    )

    op.execute(
        r"""
		ALTER TABLE abstimmung RENAME TO beschlussfassung;
		"""
    )

    op.execute(
        r"""
            CREATE PROCEDURE import_beschlussfassungen(
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
                        
                        
                DROP TABLE IF EXISTS temp_new_beschlussfassungen;
                CREATE TEMPORARY TABLE temp_new_beschlussfassungen AS 
                WITH new_beschlussfassungen AS (	
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
                FROM new_beschlussfassungen;
                
                INSERT INTO public.BESCHLUSSFASSUNG (
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
                FROM temp_new_beschlussfassungen
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
		DROP PROCEDURE import_beschlussfassungen(TEXT[], TEXT[]);
        """
    )

    op.execute(
        r"""
		ALTER TABLE beschlussfassung RENAME TO abstimmung;
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
