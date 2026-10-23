import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;

public class ExportFunctionInventory extends GhidraScript {
    public void run() throws Exception
    {
        Path output = Path.of(getScriptArgs().length == 0 ? ".local/function_inventory.txt"
                                                          : getScriptArgs()[0]);
        long count = 0;
        long fragmented = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8))
        {
            writer.write("# Ghidra-reported function bodies, not original object file splits\n");
            writer.write("# start end_exclusive body_bytes contiguous ghidra_name\n");
            for (Function f : currentProgram.getFunctionManager().getFunctions(true))
            {
                if (monitor.isCancelled())
                {
                    throw new IllegalStateException("inventory export interrupted");
                }
                long start = f.getEntryPoint().getOffset();
                long end = f.getBody().getMaxAddress().getOffset() + 1;
                long size = f.getBody().getNumAddresses();
                boolean contiguous =
                    f.getBody().getMinAddress().equals(f.getEntryPoint()) && size == end - start;
                if (!contiguous)
                    fragmented++;
                writer.write(String.format("0x%08X 0x%08X %d %s %s\n", start, end, size,
                                           contiguous ? "yes" : "no", f.getName()));
                count++;
            }
        }
        println("FUNCTION_INVENTORY_WRITTEN " + output);
        println("FUNCTION_INVENTORY_COUNT " + count + " fragmented=" + fragmented);
    }
}
