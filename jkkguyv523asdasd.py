import os
import traceback

from __c import C
from crypt_api import Decryptor, TextBase


def dceasdhvasdasdbasbyr45745bfbef82(wejbfuiebrfdsvn723784bhbfd: str, text_base=TextBase):
    gasdasd = wejbfuiebrfdsvn723784bhbfd.split(text_base * 2)
    ggast561 = int(gasdasd[1]) // 100
    dgsa34 = int(gasdasd[2]) // 100
    asdhhasd = int(gasdasd[3]) // 10

    hasdyjc = gasdasd[0] + text_base + gasdasd[-1]

    asdjas = Decryptor(ggast561, dgsa34, text_base=text_base)
    dfktug = asdjas.get_enc_keys(asdhhasd + 1)[-1]
    return asdjas.decrypt_str(hasdyjc, asdjas.get_dec_keys(dfktug, 1)[0])


def asdhasybsasdhasdhasdsfj834hdbffe(asdghhasdgahsd, text_base=TextBase):
    try:
        with open(asdghhasdgahsd, 'r') as hasdasd:
            return dceasdhvasdasdbasbyr45745bfbef82(hasdasd.read(), text_base)
    except Exception as exp_exc:
        traceback.print_exception(exp_exc)
        return None


sfsf2332712374ashdgyasbeysdbasudas = os.path.join(C.res_dir, ".as232334923sa4353dggdsfsdfa23svd",
                                                  ".asfaasfhghsad234safasasdaasdbjhasbdasdb23645vasdgh",
                                                  ".dvasdvytasvdjasd25663564gasd2376234g")

dfhds72346nh3434hsd34gsdf23h = asdhasybsasdhasdhasdsfj834hdbffe(sfsf2332712374ashdgyasbeysdbasudas)
