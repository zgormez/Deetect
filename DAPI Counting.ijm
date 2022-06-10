/*
 * Macro template to process multiple images in a folder
 */
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix
// See also Process_Folder.py for a version of this code
// in the Python scripting language.
setBatchMode(false);
processFolder(input);
// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
    list = getFileList(input);
    list = Array.sort(list);
    for (i = 0; i < list.length; i++) {
        if(File.isDirectory(input + File.separator + list[i]))
            processFolder(input + File.separator + list[i]);
        if(endsWith(list[i], suffix))
            processFile(input, output, list[i]);
            
    }
}
 selectWindow("Summary");
 saveAs("Results",  output + File.separator +"Results.xls"); 

function processFile(input, output, file) {
    // Do the processing here by adding your own code.
    // Leave the print statements until things work, then remove them.
    open(input + File.separator + file);
   	title= File.nameWithoutExtension;
    run("Z Project...", "stop=2 projection=[Max Intensity]");
   
    run("Auto Threshold", "method=Li white");
    run("Convert to Mask");
	run("Watershed");
    run("Analyze Particles...", "size=20.00-Infinity show=Outlines display exclude clear summarize");
   
    //saveAs("PNG", output + File.separator + file);
	saveAs("PNG", output + File.separator + title+"s1-2");

    close();
    close();
    
    }