from smarketsim.v2 import mfeature

LC_STEPS = [1, 5, 20]
LCF_STEPS = [1]
VOL_SIZES = {1: [30, 100]}
PERCS = [20, 100, 400]

DESC = {
    "LCF1": {
        "X_cols": ["LC1VOL30", "LC1VOL100", "PERC20", "PERC100", "PERC400"],
        "LC": "LC1",
        "corr_size": 100,
    }
}


def build_parq(base, parq_folder):
    mfeature.mfeat_from_base(base, LC_STEPS, LCF_STEPS, VOL_SIZES, PERCS, parq_folder)
    return
