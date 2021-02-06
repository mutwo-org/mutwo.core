from mutwo import events
from mutwo import parameters

# default values for MidiFileConverter
DEFAULT_AVAILABLE_MIDI_CHANNELS = tuple(range(16))
# standard value for most synthesizer is +/- 200 cents
DEFAULT_MAXIMUM_PITCH_BEND_DEVIATION_IN_CENTS = 200
# default to synchronous multitrack midi files
DEFAULT_MIDI_FILE_TYPE = 1
DEFAULT_MIDI_INSTRUMENT_NAME = "Acoustic Grand Piano"
DEFAULT_N_MIDI_CHANNELS_PER_TRACK = 1
DEFAULT_TEMPO_EVENTS = events.basic.SequentialEvent(
    [events.basic.EnvelopeEvent(1, parameters.tempos.TempoPoint(120, 1))]
)
DEFAULT_TICKS_PER_BEAT = 480

# midi specific constants
ALLOWED_MIDI_CHANNELS = tuple(range(16))
MAXIMUM_MICROSECONDS_PER_BEAT = 16777215
MAXIMUM_PITCH_BEND = 16382
MAXIMUM_VELOCITY = 127
# factor to multiply beats-in-seconds to get
# beats-in-microseconds (which is the tempo unit for midi)
MIDI_TEMPO_FACTOR = 1000000
MINIMUM_VELOCITY = 0
NEUTRAL_PITCH_BEND = 8191
