-- Play stage-skip code 0881 (area 2, stages 1,3,4 cleared) through its boss into area 3.
-- RAM shortcuts (they run the game's own code, nothing is faked): the stage is finished by pointing an idle task
-- (task $0C, routine $75A6) at the stage-clear entry $C4FC that the exit calls; the boss fight is ended by pointing
-- the boss task (task $02) at the hub's area-complete sequence $18DDC. Tasks: 48-byte records, pointers at $62E,
-- +4 = routine. USA addresses.
local O=(REG=="eu") and 6 or 0   -- Europe's code is 6 bytes lower here (no movem at USA $7C4A)
local function st(t) log(string.format("%-14s 953A=%d 953B=%d 953C=%d 953D=%02X lives=%d", t, r8(0x953A),r8(0x953B),r8(0x953C),r8(0x953D),r8(0x9543))) end
-- a failed check logs and quits (no error() dialog left open)
local function need(ok,msg) if not ok then log("FAIL: "..msg) client.exit() end end
local function task(i) return memory.read_u32_be(0x62E+4*i,"M68K BUS") & 0xFFFF end
need(enter("0881"),"code rejected") wait(700) tap("Start") wait(600) st("hub") shot("1_hub")
tap("A") wait(500) st("stage") shot("2_stage")
need(memory.read_u32_be(task(0x0C)+4,DOMAIN)==0x75A6, "task 0C not idle")
memory.write_u32_be(task(0x0C)+4,0xC4FC-O,DOMAIN)
wait(1100) st("cleared") shot("3_boss")
need(memory.read_u32_be(task(2)+4,DOMAIN)==0x15144-O, "boss task not found")
memory.write_u32_be(task(2)+4,0x18DDC-O,DOMAIN)
wait(1400) st("planet") shot("4_planet")
tap("Start") wait(500) st("area 3 hub") shot("5_hub3")
tap("A") wait(500) st("area 3 stage") shot("6_stage3")
