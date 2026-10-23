import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.SourceType;

public class LabelMovementCounter extends GhidraScript {
    private static final String[][] FUNCTIONS = {
        {"022b3024", "PlayerMovementCounter_ctorCandidate", "92", "mfspr", "blr"},
        {"022b3080", "PlayerMovementCounter_bindDependencies", "24", "stw", "blr"},
        {"022b3098", "PlayerMovementCounter_updateCandidate", "432", "mfspr", "blr"},
        {"022b3248", "PlayerMovementCounter_getRatioCandidate", "192", "mfspr", "blr"},
        {"022b3308", "PlayerMovementCounter_isAtLimitCandidate", "76", "mfspr", "blr"}
    };

    public void run() throws Exception {
        for (String[] item : FUNCTIONS) {
            Address entry = toAddr(item[0]);
            String name = item[1];
            int size = Integer.parseInt(item[2]);
            Function function = getFunctionAt(entry);
            if (function == null || function.getBody().getNumAddresses() != size) {
                throw new IllegalStateException(name + " has unexpected function bounds");
            }
            Instruction first = getInstructionAt(entry);
            Instruction last = getInstructionAt(entry.add(size - 4));
            if (first == null || last == null ||
                !item[3].equals(first.getMnemonicString()) ||
                !item[4].equals(last.getMnemonicString())) {
                throw new IllegalStateException(name + " has unexpected PPC instructions");
            }
            if (!function.getName().equals(name)) {
                if (!function.getName().startsWith("FUN_")) {
                    throw new IllegalStateException(name + " would replace " + function.getName());
                }
                function.setName(name, SourceType.USER_DEFINED);
            }
            println("LABEL " + name + " " + entry + " size=" + size);
        }
        println("MOVEMENT_COUNTER_LABELS_DONE");
    }
}
