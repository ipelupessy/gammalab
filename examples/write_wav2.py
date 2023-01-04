from gammalab import main
from gammalab.acquisition import FileReplay
from gammalab.transform import Float2Int16
from gammalab.backend import SaveWav

soundcard=FileReplay("background.20221120144917", realtime=False)
convert=Float2Int16()
save=SaveWav("test.wav")

soundcard.plugs_into(convert)
convert.plugs_into(save)

main()
