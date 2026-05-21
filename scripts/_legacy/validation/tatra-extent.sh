# Tatras WGS84 extent — single source of truth for geographic validation.
# Sourced by check-coordinates.sh and check-exports.sh.
#
# LON/LAT: Western Tatras coverage, no safety margin (current data fits inside).
# ELEV: 850 m derived from PIG lowest Tatra cave entrance (Jaskinia
# Jaszczurowska Wodna, 915 m) with a small margin; 2655 m = Gerlach,
# highest Tatra peak.
TATRA_LON_MIN=19.80
TATRA_LON_MAX=20.10
TATRA_LAT_MIN=49.20
TATRA_LAT_MAX=49.30
TATRA_ELEV_MIN=850
TATRA_ELEV_MAX=2655
