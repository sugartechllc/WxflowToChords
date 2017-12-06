import machine
#
# The voltage divider is 115k ohms/56k ohms = 0.3275
#
# The attenuation will be 2.5db = 0.562
#
# The ADC has a range of 12 bits, or 4095 over 1V
# Each ADC count = 1/4095 = 0.0002442
#
# VBATT = (counts * 0.0002442) / (0.3275 * 0.562)
#       = counts * 0.0013
#
def battv():
    adc  = machine.ADC()
    apin = adc.channel(pin="P16", attn=machine.ADC.ATTN_2_5DB)
    return apin() * 0.0013

def toChords(config):
    """Create a CHORDS record.

    The config should contain a "wipy_report" entry. If
    not, an empty record is returned.

    The config should contain:
    {
      "skey": "the key",
      "wipy_report": {
        "_enabled": true,
        "_chords_inst_id": "chords_instrument_id",
        "_battv" : "chords_short_name_for_wipy_voltage"
      }
    }
    """
    chords_record = {}
    if "wipy_report" not in config:
        return chords_record
    wipy_report = config["wipy_report"]
    if not wipy_report["_enabled"]:
        return chords_record

    v = battv()
    v_s = str(v)
    vars = {}
    vars[wipy_report["_battv"]] = v_s
    chords_record["inst_id"] = wipy_report["_chords_inst_id"]
    chords_record["skey"]    = config["skey"]
    chords_record["vars"]    = vars

    return chords_record