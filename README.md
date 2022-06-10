# deep learning-based all-in-one image analysis tool for cell quantification
an automated deep learning-based all-in-one image processing pipeline for image sequences of the examined ECMO-membranes to quantify cell depositions in certain areas and identify predilection sites for increased cell adherence. 

## publications
* This study is a part of PHD. 
* This study was presented at the GCB 2021, Germany. You can find the submitted abstract [here](https://github.com/zgormez/TH-BINGEN_ECMO_AI/blob/main/papers/GCB_2021_G%C3%B6rmez_Hoeren_Richter_Krause_Troidl.pdf).

## dataset
you can find the 100 images which were used to test.  
@Felix add hre some explanation for each part of the image name. What is their meaning?

## Tools
### Conventional Segmentation and Counting via FIJI 
In this approach a macro was programmed in FIJI to automatically quantify the cell count. It was written in Image-J macro script language. In the first two steps, the images were automatically thresholded using the Li-white method [13]. It was used to set a threshold for the intensity and remove background noise and artifacts from the image to emphasise the cell nucleus structures. Since areas of increased nucleus density lose their differentiability using a threshold the watershed tool was used in the next step. In this morphological process a topographic map of the image is virtually flooded and wherev-er two watersheds meet, the method assumes two contiguous cell cores and draws a di-viding line between the touching objects. The final step of the macro was the counting of the cell nuclei via the analyze-particles function. It scans the image until it detects the edge of an object. It outlines the object boundaries and measures the area. The steps are repeated until the entire image is scanned. 
The minimum size of the objects to be counted was set to 20 pixels2. The roundness (cir-cularity) of the objects to be detected was set to was set to 0 - 1 due to the different shapes of the cell nuclei. After execution of the function, the result is displayed as an overview drawing with a representation of the object outlines and a result table. 
You can find the FIJI macro [here](https://github.com/zgormez/TH-BINGEN_ECMO_AI/blob/main/DAPI%20Counting.ijm)
![macro workflow](https://github.com/zgormez/TH-BINGEN_ECMO_AI/blob/main/images/macro_workflow.png)

### AI-based tool
Especially in highly aggregated areas of the investigated samples, only a low dif-ferentiation of individual cell nuclei could be expected using the conventional semantic segmentation applied in FIJI. An AI-based method was developed to better resolve these areas, as it was expected to perform better than conventional segmentation [14]. Never-theless, a central problem in applying these methods is that they involve many sub-processes (pre-, main-, post-processing) that are difficult to modulate by scientists that are inexperienced in programming.
To solve this gap, an automated, compact, deep learning-based ready-to-use image processing tool (ConfoQuant) was developed for the quantification process. It has a graphical user interface (GUI) and many different features to handle problems that oc-curred during the quantification process. 
![AI_tool workflow](https://github.com/zgormez/TH-BINGEN_ECMO_AI/blob/main/images/AI_tool_workflow.png)
