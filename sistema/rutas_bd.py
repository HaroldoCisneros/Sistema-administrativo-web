"""
sistema/rutas_bd.py
===================

Le dice a Django en qué base de datos va cada cosa.

    - Las tablas propias del sistema (usuarios, sesiones, empresas y las que
      agreguen los módulos en el futuro) van SIEMPRE a la base 'default'
      (SIGHEC).
    - La base 'usuarios' (MasterProfit) y las bases de Profit de cada empresa
      (conexiones "profit_<CODIGO>", ver nucleo/profit.py) solo se consultan
      con SQL directo, y Django tiene prohibido crear o modificar tablas en
      ellas (allow_migrate devuelve False).
"""


class RutasBD:
    # Base de Profit a la que Django nunca le crea ni cambia tablas.
    SOLO_CONSULTA = {"usuarios"}
    # Las conexiones a las bases de Profit de cada empresa empiezan con esto.
    PREFIJO_EMPRESA = "profit_"

    def db_for_read(self, model, **hints):
        """Base donde Django LEE los modelos propios: siempre 'default'."""
        return "default"

    def db_for_write(self, model, **hints):
        """Base donde Django ESCRIBE los modelos propios: siempre 'default'."""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Permite relaciones entre modelos propios."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        'migrate' crea/actualiza tablas. Solo se permite en la base propia;
        en las de Profit, nunca.
        """
        return db not in self.SOLO_CONSULTA and not db.startswith(self.PREFIJO_EMPRESA)
