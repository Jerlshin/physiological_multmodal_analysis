"""Frozen feature dictionary (protocol §6): reference-free (RF), synchrony (SYN), quality (Q), covariates (C)."""

# Block structure used by the model families (protocol §9; evaluation contract §5).
RF_BLOCKS = {
    "RF_EEG": ["RF1_eeg_posterior_alpha", "RF2_eeg_frontal_theta"],
    "RF_ECG": ["RF3_heart_rate", "RF4_ln_rmssd"],
    "RF_GAZE": ["RF5_gaze_dispersion", "RF6_saccade_rate"],
    "RF_PUPIL": ["RFP_pupil_variability"],
}
SYN_BLOCKS = {
    "SYN_EEG": ["SYN1_eeg_isc"],
    "SYN_ECG": ["SYN2_hr_isc"],
    "SYN_GAZE": ["SYN3_gaze_isc"],
    "SYN_PUPIL": ["SYNP_pupil_isc"],
}
Q_COLUMNS = ["Q_gaze_correction", "Q_pupil_correction", "Q_pupil_absent", "Q_eeg_zeroed", "Q_eeg_16hz_excess"]
Q_COLUMNS_E1 = ["Q_gaze_correction", "Q_pupil_correction", "Q_pupil_absent"]
C_COLUMNS = ["C_age", "C_sex_male", "C_sex_unknown", "C_asrs_inattention", "C_asrs_hyperactivity",
             "C_digit_span", "C_digit_span_missing"]
C_COLUMNS_E1 = ["C_age", "C_sex_male", "C_sex_unknown"]
GPA_COLUMNS = ["C_gpa", "C_gpa_missing"]

MODALITY_OF_BLOCK = {"RF_EEG": "eeg", "RF_ECG": "ecg", "RF_GAZE": "gaze", "RF_PUPIL": "pupil",
                     "SYN_EEG": "eeg", "SYN_ECG": "ecg", "SYN_GAZE": "gaze", "SYN_PUPIL": "pupil"}
