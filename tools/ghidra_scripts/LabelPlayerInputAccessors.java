import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.SourceType;

public class LabelPlayerInputAccessors extends GhidraScript {
    private static final String[][] FUNCTIONS = {
        {"022b2f64", "PlayerInput_disableJumpButton", "12", "li", "blr"},
        {"022b2f70", "PlayerInput_enableJumpButton", "12", "li", "blr"},
        {"022b2f7c", "PlayerInput_isStickOn", "8", "lbz", "blr"},
        {"022b2f84", "PlayerInput_getMoveVec", "8", "addi", "blr"},
        {"022b2f8c", "PlayerInput_getMoveVecNoArrange", "8", "addi", "blr"},
        {"022b2f94", "PlayerInput_getStickX", "8", "lfs", "blr"},
        {"022b2f9c", "PlayerInput_getStickY", "8", "lfs", "blr"},
        {"022b2fa4", "PlayerInput_getFrameFromLastJumpTrig", "8", "lwz", "blr"},
        {"022b2fac", "PlayerInput_isJumpButtonOn", "8", "lbz", "blr"},
        {"022b2fb4", "PlayerInput_isDashTrigOn", "8", "lbz", "blr"},
        {"022b2fbc", "PlayerInput_isDashButtonOn", "8", "lbz", "blr"},
        {"022b2fc4", "PlayerInput_isDashButtonReleased", "8", "lbz", "blr"},
        {"022b2fcc", "PlayerInput_isSquatTrigOn", "8", "lbz", "blr"},
        {"022b2fd4", "PlayerInput_isSquatButtonOn", "8", "lbz", "blr"},
        {"022b2fdc", "PlayerInput_isHipDropTrigOn", "8", "lbz", "blr"},
        {"022b2fe4", "PlayerInput_isHipDropButtonOn", "8", "lbz", "blr"},
        {"022b2fec", "PlayerInput_isFireBallTrigOn", "8", "lbz", "blr"},
        {"022b2ff4", "PlayerInput_isSwimPaddleTrigOn", "8", "lbz", "blr"},
        {"022b2ffc", "PlayerInput_isBubbleTrigOn", "8", "lbz", "blr"},
        {"022b3004", "PlayerInput_isClimbAttackTrigOn", "8", "lbz", "blr"},
        {"022b300c", "PlayerInput_isClimbAttackButtonOn", "8", "lbz", "blr"},
        {"022b3014", "PlayerInput_isHoldButtonOn", "8", "lbz", "blr"},
        {"022b301c", "PlayerInput_isReleaseTrigOn", "8", "lbz", "blr"}
    };

    public void run() throws Exception {
        for (String[] item : FUNCTIONS) {
            Address entry = toAddr(item[0]);
            String name = item[1];
            int size = Integer.parseInt(item[2]);
            Address end = entry.add(size - 1);
            if (getInstructionAt(entry) == null) disassemble(entry);
            if (getInstructionAt(end.subtract(3)) == null) disassemble(end.subtract(3));
            Instruction first = getInstructionAt(entry);
            Instruction last = getInstructionAt(end.subtract(3));
            if (first == null || last == null ||
                !first.getMnemonicString().equals(item[3]) ||
                !last.getMnemonicString().equals(item[4])) {
                throw new IllegalStateException(name + " has unexpected instructions");
            }
            Function function = getFunctionAt(entry);
            Function overlapping = getFunctionContaining(entry);
            if (function == null && overlapping != null) {
                throw new IllegalStateException(name + " overlaps " + overlapping.getName());
            }
            if (function == null) {
                function = currentProgram.getFunctionManager().createFunction(
                    name, entry, new AddressSet(entry, end), SourceType.USER_DEFINED);
            }
            if (function == null || function.getBody().getNumAddresses() != size) {
                throw new IllegalStateException(name + " has unexpected body boundaries");
            }
            if (!function.getName().equals(name)) {
                if (!function.getName().startsWith("FUN_")) {
                    throw new IllegalStateException(name + " already labeled " + function.getName());
                }
                function.setName(name, SourceType.USER_DEFINED);
            }
            println("LABELED " + function.getName() + " " + entry + " size=" + size);
        }
        println("INPUT_ACCESSOR_LABELS_DONE");
    }
}
