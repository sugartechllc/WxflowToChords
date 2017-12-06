import machine


def battv():
    adc  = machine.ADC()
    apin = adc.channel(pin="P16", attn=machine.ADC.ATTN_11DB)
    # empirically determined value of volts per count.
    return apin() * 0.00275

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