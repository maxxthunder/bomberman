-- JP "Tap is not connected" screen: Battle Game's entry (bank 7 $A6F5) tests pad 5's held buttons ($2036 & $1F = $1F:
-- Up+I+II+Select+Run). Mesen's test runner can't drive pad 5, so the byte is written just before the test runs.
at(function() on_exec(0xA707,7,function() wr(0x2036,0x1F) print('pad 5 byte set at',FRAME) end)
  on_exec(0xA712,7,function() print('error-screen path taken at',FRAME) after(60,function() shot('tap_error_jp') end) end) end)
wait(400) press({run=true}) wait(400) press({down=true}) wait(20) press({run=true}) wait(300)
