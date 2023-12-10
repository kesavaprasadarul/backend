"""Make fks cascade

Revision ID: 168b8f28461f
Revises: 38a83e5e443b
Create Date: 2023-12-10 12:40:43.982063

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '168b8f28461f'
down_revision: Union[str, None] = '38a83e5e443b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # recreate fks with cascade
    # for each table we first drop the fk and then recreate it with cascade

    ### These ones are all cascade on update and set null on delete since they
    ### have multiple parents and we don't want to delete the children when one
    ### parent is deleted

    ##  fundstelle

    # fundstelle->drucksache
    op.drop_constraint(
        constraint_name="fundstelle_drucksache_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="fundstelle_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # fundstelle->plenarprotokoll
    op.drop_constraint(
        constraint_name="fundstelle_plenarprotokoll_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="fundstelle_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # fundstelle->vorgangsposition
    op.drop_constraint(
        constraint_name="fundstelle_vorgangsposition_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="fundstelle_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # ressort

    # ressort->drucksache
    op.drop_constraint(
        constraint_name="ressort_drucksache_id_fkey",
        table_name="ressort",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="ressort_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ressort",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # ressort->vorgangsposition
    op.drop_constraint(
        constraint_name="ressort_vorgangsposition_id_fkey",
        table_name="ressort",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="ressort_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ressort",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # urheber

    # urheber->drucksache
    op.drop_constraint(
        constraint_name="urheber_drucksache_id_fkey",
        table_name="urheber",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="urheber_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="urheber",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # urheber->vorgangsposition
    op.drop_constraint(
        constraint_name="urheber_vorgangsposition_id_fkey",
        table_name="urheber",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="urheber_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="urheber",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # vorgangsbezug

    # vorgangsbezug->drucksache
    op.drop_constraint(
        constraint_name="vorgangsbezug_drucksache_id_fkey",
        table_name="vorgangsbezug",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgangsbezug_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangsbezug",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # vorgangsbezug->plenarprotokoll
    op.drop_constraint(
        constraint_name="vorgangsbezug_plenarprotokoll_id_fkey",
        table_name="vorgangsbezug",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgangsbezug_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangsbezug",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    ## vorgang

    # vorgang->drucksache
    op.drop_constraint(
        constraint_name="vorgang_drucksache_id_fkey",
        table_name="vorgang",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgang_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    # vorgang->plenarprotokoll
    op.drop_constraint(
        constraint_name="vorgang_plenarprotokoll_id_fkey",
        table_name="vorgang",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgang_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    ### These ones are all cascade on update and cascade on delete since they
    ### have only one parent and we want to delete the children when the parent
    ### is deleted

    ## drucksache

    # autor->drucksache
    op.drop_constraint(
        constraint_name="autor_drucksache_id_fkey",
        table_name="autor",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="autor_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="autor",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # drucksache-text->drucksache
    op.drop_constraint(
        constraint_name="drucksache_text_drucksache_id_fkey",
        table_name="drucksache_text",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="drucksache_text_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="drucksache_text",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    ## plenarprotokoll

    # plenarprotokoll-text->plenarprotokoll
    op.drop_constraint(
        constraint_name="plenarprotokoll_text_plenarprotokoll_id_fkey",
        table_name="plenarprotokoll_text",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="plenarprotokoll_text_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="plenarprotokoll_text",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    ## vorgang

    # vorgang_deskriptor->vorgang
    op.drop_constraint(
        constraint_name="vorgang_deskriptor_vorgang_id_fkey",
        table_name="vorgang_deskriptor",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgang_deskriptor_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang_deskriptor",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # verkuendung->vorgang
    op.drop_constraint(
        constraint_name="verkuendung_vorgang_id_fkey",
        table_name="verkuendung",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="verkuendung_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="verkuendung",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # inkratfttreten->vorgang
    op.drop_constraint(
        constraint_name="inkrafttreten_vorgang_id_fkey",
        table_name="inkrafttreten",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="inkrafttreten_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="inkrafttreten",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # vorgang_verlinkung->vorgang
    op.drop_constraint(
        constraint_name="vorgang_verlinkung_vorgang_id_fkey",
        table_name="vorgang_verlinkung",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgang_verlinkung_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang_verlinkung",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    ## vorgangsposition

    # ueberweisung->vorgangsposition
    op.drop_constraint(
        constraint_name="ueberweisung_vorgangsposition_id_fkey",
        table_name="ueberweisung",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="ueberweisung_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ueberweisung",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # aktivitaet_anzeige->vorgangsposition
    op.drop_constraint(
        constraint_name="aktivitaet_anzeige_vorgangsposition_id_fkey",
        table_name="aktivitaet_anzeige",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="aktivitaet_anzeige_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="aktivitaet_anzeige",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # beschlussfassung->vorgangsposition
    op.drop_constraint(
        constraint_name="beschlussfassung_vorgangsposition_id_fkey",
        table_name="beschlussfassung",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="beschlussfassung_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="beschlussfassung",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # vorgangspositionbezug->vorgangsposition
    op.drop_constraint(
        constraint_name="vorgangspositionbezug_vorgangsposition_id_fkey",
        table_name="vorgangspositionbezug",
        type_="foreignkey",
        schema="dip",
    )
    op.create_foreign_key(
        constraint_name="vorgangspositionbezug_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangspositionbezug",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # only now can we make the columns nullable since then a downgrade will work with the new fks

    op.alter_column(
        table_name='vorgang',
        column_name='aktualisiert',
        nullable=True,
        schema='dip',
    )

    op.alter_column(
        table_name='vorgangsposition',
        column_name='aktualisiert',
        nullable=True,
        schema='dip',
    )


def downgrade() -> None:
    op.execute("""DELETE FROM dip.vorgangsposition WHERE aktualisiert IS NULL;""")

    op.alter_column(
        table_name='vorgangsposition',
        column_name='aktualisiert',
        nullable=False,
        schema='dip',
    )

    op.execute(""" DELETE FROM dip.vorgang WHERE aktualisiert IS NULL;""")

    op.alter_column(
        table_name='vorgang',
        column_name='aktualisiert',
        nullable=False,
        schema='dip',
    )

    op.drop_constraint(
        constraint_name="vorgangspositionbezug_vorgangsposition_id_fkey",
        table_name="vorgangspositionbezug",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgangspositionbezug_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangspositionbezug",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="beschlussfassung_vorgangsposition_id_fkey",
        table_name="beschlussfassung",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="beschlussfassung_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="beschlussfassung",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="aktivitaet_anzeige_vorgangsposition_id_fkey",
        table_name="aktivitaet_anzeige",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="aktivitaet_anzeige_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="aktivitaet_anzeige",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="ueberweisung_vorgangsposition_id_fkey",
        table_name="ueberweisung",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="ueberweisung_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ueberweisung",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgang_verlinkung_vorgang_id_fkey",
        table_name="vorgang_verlinkung",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgang_verlinkung_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang_verlinkung",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="inkrafttreten_vorgang_id_fkey",
        table_name="inkrafttreten",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="inkrafttreten_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="inkrafttreten",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="verkuendung_vorgang_id_fkey",
        table_name="verkuendung",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="verkuendung_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="verkuendung",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgang_deskriptor_vorgang_id_fkey",
        table_name="vorgang_deskriptor",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgang_deskriptor_vorgang_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang_deskriptor",
        referent_table="vorgang",
        local_cols=["vorgang_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="plenarprotokoll_text_plenarprotokoll_id_fkey",
        table_name="plenarprotokoll_text",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="plenarprotokoll_text_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="plenarprotokoll_text",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="drucksache_text_drucksache_id_fkey",
        table_name="drucksache_text",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="drucksache_text_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="drucksache_text",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="autor_drucksache_id_fkey",
        table_name="autor",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="autor_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="autor",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgang_plenarprotokoll_id_fkey",
        table_name="vorgang",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgang_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgang_drucksache_id_fkey",
        table_name="vorgang",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgang_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgang",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgangsbezug_plenarprotokoll_id_fkey",
        table_name="vorgangsbezug",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgangsbezug_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangsbezug",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="vorgangsbezug_drucksache_id_fkey",
        table_name="vorgangsbezug",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="vorgangsbezug_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="vorgangsbezug",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="urheber_vorgangsposition_id_fkey",
        table_name="urheber",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="urheber_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="urheber",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="urheber_drucksache_id_fkey",
        table_name="urheber",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="urheber_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="urheber",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="ressort_vorgangsposition_id_fkey",
        table_name="ressort",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="ressort_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ressort",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="ressort_drucksache_id_fkey",
        table_name="ressort",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="ressort_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="ressort",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="fundstelle_vorgangsposition_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="fundstelle_vorgangsposition_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="vorgangsposition",
        local_cols=["vorgangsposition_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="fundstelle_plenarprotokoll_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="fundstelle_plenarprotokoll_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="plenarprotokoll",
        local_cols=["plenarprotokoll_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )

    op.drop_constraint(
        constraint_name="fundstelle_drucksache_id_fkey",
        table_name="fundstelle",
        type_="foreignkey",
        schema="dip",
    )

    op.create_foreign_key(
        constraint_name="fundstelle_drucksache_id_fkey",
        source_schema="dip",
        referent_schema="dip",
        source_table="fundstelle",
        referent_table="drucksache",
        local_cols=["drucksache_id"],
        remote_cols=["id"],
        onupdate="NO ACTION",
        ondelete="NO ACTION",
    )
