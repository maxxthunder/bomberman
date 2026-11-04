-- Make the savestates the other scripts load: pw.mst = PASSWORD screen, cursor on the first digit, all digits 0.
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
press({down=true},8) wait(20) press({down=true},8) wait(20) press({run=true},8) wait(200)
at(function() shot('pw') end) savefile('pw.mst')
