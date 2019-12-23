from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import SaveWav

soundcard=SoundCard(sample_format="int16")
save=SaveWav()

soundcard.plugs_into(save)

main(10)
