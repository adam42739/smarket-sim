from smarketsim.v2 import mfeature

LC_STEPS = [1]
LCF_STEPS = [1]
VOL_SIZES = {1: [30, 100, 400]}
PERCS = [5, 20, 100, 200, 400]

DESC = {
    "LCF1": {
        "X_cols": [
            "LC1VOL30",
            "LC1VOL100",
            "LC1VOL400",
            "PERC5",
            "PERC20",
            "PERC100",
            "PERC200",
            "PERC400",
        ],
        "LC": "LC1",
        "corr_size": 100,
    }
}


def build_parq(base, parq_folder):
    mfeature.mfeat_from_base(base, LC_STEPS, LCF_STEPS, VOL_SIZES, PERCS, parq_folder)
    return
