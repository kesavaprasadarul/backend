"""Add import procedures

Revision ID: 38a83e5e443b
Revises: f8c93790f568
Create Date: 2023-12-10 12:07:05.573654

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '38a83e5e443b'
down_revision: Union[str, None] = 'f8c93790f568'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
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
				SELECT '2023-01-01'::DATE  AS date_from
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
				JOIN dip.VORGANG V ON D.id = V.drucksache_id 
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


def downgrade() -> None:
    op.execute(
        """
        DROP FUNCTION count_weekly_drucksache(DATE, DATE, TEXT[], TEXT[]);
        """
    )
