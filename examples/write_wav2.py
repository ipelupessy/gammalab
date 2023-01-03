from gammalab import main
from gammalab.acquisition import FileReplay
from gammalab.transform import Raw2Float, Float2Int16, Int162Raw
from gammalab.backend import SaveWav

soundcard=FileReplay("background.20221120144917", realtime=False)
convert1=Raw2Float()
convert2=Float2Int16()
convert3=Int162Raw()
save=SaveWav("test.wav")


soundcard.plugs_into(convert1)
convert1.plugs_into(convert2)
convert2.plugs_into(convert3)
convert3.plugs_into(save)

main(10)
