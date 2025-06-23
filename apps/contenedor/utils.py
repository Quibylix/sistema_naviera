# apps/contenedor/utils.py
BULTOS_POR_CARGA = {
    1: [1, 5],            # perecedera            -> Caja, Bolsa
    2: [1, 2, 9],         # general               -> Caja, Pallet, Bobina
    3: [4, 10],           # peligrosa             -> Tambor, Bidón
    4: [1, 5],            # refrigerada aliment.  -> Caja, Bolsa
    5: [4],               # automóviles           -> (sin bulto) o Tambor si liquido
    6: [5, 7],            # sobredimensionada     -> Lona, Rollo
    7: [5],               # granel sólido         -> Bolsa
    8: [1, 2],            # electrónicos / tech   -> Caja, Pallet
}
