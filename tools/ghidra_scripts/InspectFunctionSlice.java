import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;

public class InspectFunctionSlice extends GhidraScript {
    public void run() throws Exception
    {
        String[] requests = getScriptArgs();
        if (requests.length == 0)
        {
            throw new IllegalArgumentException("Pass one or more function entry addresses");
        }
        DecompInterface decompiler = new DecompInterface();
        decompiler.toggleCCode(true);
        if (!decompiler.openProgram(currentProgram))
        {
            throw new IllegalStateException("Decompiler unavailable");
        }
        for (String value : requests)
        {
            Address address = toAddr(value);
            Function function = getFunctionAt(address);
            println("=== ENTRY " + value + " ===");
            if (function == null)
            {
                println("NO_FUNCTION " + value);
                continue;
            }
            println("NAME " + function.getName());
            println("BODY_BYTES " + function.getBody().getNumAddresses());
            println("ENTRY " + function.getEntryPoint());
            Instruction instruction = getInstructionAt(address);
            int printed = 0;
            while (instruction != null && function.getBody().contains(instruction.getAddress()) &&
                   printed < 64)
            {
                println("ASM " + instruction.getAddress() + " " + instruction.toString());
                printed++;
                instruction = instruction.getNext();
            }
            int callers = 0;
            for (Reference reference : getReferencesTo(address))
            {
                if (callers++ >= 16)
                    break;
                Function parent = getFunctionContaining(reference.getFromAddress());
                println("XREF " + reference.getFromAddress() + " " + reference.getReferenceType() +
                        " " + (parent == null ? "<none>" : parent.getName()));
            }
            DecompileResults result = decompiler.decompileFunction(function, 12, monitor);
            if (result.decompileCompleted() && result.getDecompiledFunction() != null)
            {
                String code = result.getDecompiledFunction().getC();
                println("C_START\n" + code.substring(0, Math.min(code.length(), 8000)) + "\nC_END");
            } else
            {
                println("DECOMP_FAIL " + result.getErrorMessage());
            }
        }
        decompiler.dispose();
        println("INSPECTION_DONE");
    }
}
