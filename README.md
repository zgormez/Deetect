# Deetect:
## a deep learning based image analysis tool for quantification of adherent cell populations on oxygenator membranes after extracorporeal membrane oxygenation therapy
an automated deep learning-based all-in-one image processing pipeline for image sequences of the examined ECMO-membranes to quantify cell depositions in certain areas and identify predilection sites for increased cell adherence. 

## Table of Content

  * [Experimental dataset](#experimental-dataset)
  * [Tools](#tools)
    + [Conventional Segmentation and Counting via FIJI](#conventional-segmentation-and-counting-via-fiji)
    + [Deetect: deep learning based image analysis tool](#deetect-deep-learning-based-image-analysis-tool)
  * [Deetect Development](#deetect-development)
  * [How to get started](#how-to-get-started)
  * [Usage](#usage)
    + [Main Window](#main-window)
    + [Stats Window](#stats-window)
  * [Input-Outputs](#input--outputs)
    + [Minimal Dataset including input and outputs](#minimal-dataset-including-input-and-outputs)
    + [Input](#input)
    + [Outputs](#outputs)
  * [publications](#publications)
 
 
## Experimental dataset
This dataset is available at: https://edmond.mpdl.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.2OEMSK  
The experiment was done in four sets, 115 images are generated. The number of images produced in each set is as follows: 
- Set 1 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator 
- Set 2 contains 25 imagesequences; 10 from Fiber, 15 from Warp predilection site;   10 from venous (I), 6  from middle (M) and 9 from Arterial (A) part of the oxygenator
- Set 3 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator
- Set 4 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator


## Tools
### Conventional Segmentation and Counting via FIJI 
In this approach a macro was programmed in FIJI to automatically quantify the cell count. It was written in Image-J macro script language. In the first two steps, the images were automatically thresholded using the Li-white method [13]. It was used to set a threshold for the intensity and remove background noise and artifacts from the image to emphasise the cell nucleus structures. Since areas of increased nucleus density lose their differentiability using a threshold the watershed tool was used in the next step. In this morphological process a topographic map of the image is virtually flooded and wherev-er two watersheds meet, the method assumes two contiguous cell cores and draws a di-viding line between the touching objects. The final step of the macro was the counting of the cell nuclei via the analyze-particles function. It scans the image until it detects the edge of an object. It outlines the object boundaries and measures the area. The steps are repeated until the entire image is scanned. 
The minimum size of the objects to be counted was set to 20 pixels2. The roundness (cir-cularity) of the objects to be detected was set to was set to 0 - 1 due to the different shapes of the cell nuclei. After execution of the function, the result is displayed as an overview drawing with a representation of the object outlines and a result table. 
You can find the FIJI macro [here](DAPI%20Counting.ijm)
![Makro workflow](https://user-images.githubusercontent.com/107420190/191925245-eebd4790-2f81-4d38-ad59-e1392bf858a4.png)


### Deetect: deep learning based image analysis tool

Especially in highly aggregated areas of the investigated samples, only a low differentiation of individual cell nuclei could be expected using the conventional semantic segmentation applied in FIJI. An AI-based method was developed to better resolve these areas, as it was expected to perform better than conventional segmentation [14]. Never-theless, a central problem in applying these methods is that they involve many sub-processes (pre-, main-, post-processing) that are difficult to modulate by scientists that are inexperienced in programming.
To solve this gap, an automated, compact, deep learning-based ready-to-use image processing tool (Deetect) was developed for the quantification process. It has a graphical user interface (GUI) and many different features to handle problems that occurred during the quantification process. 
![Deetect workflow](/images/Deetect_workflow_09.22.png)

## Deetect Development

Deetect was written in Python version 3.8. It is developed with open-source packages available for Python. The required packages are specified in the ['deetect_env.yml'](Deetect/deetect_env.yml) file. In the ['How to get started'](#how-to-get-started) section of this readme, it is explained how to install them with the package manager conda. 
The required computation time is essentially defined by the segmentation step performed via Cellpose and varies greatly with the cell size and population shown. Thus the time depends on Cellpose performance and the capacity of the used computer which has  GPU or CPU.  
2-z-substack analysis of 100 images took about 200 minutes (2 minutes per image) on a laptop equipped with an NVIDIA Quadro T2000

## How to get started

1. Install an [Anaconda](https://www.anaconda.com/download/) distribution of Python -- Choose **Python 3.8** and your operating system.
2. Download Deetect [Deetect file](Deetect)
3. Open an anaconda prompt and create a new environment with `conda env create --file deetect_env.yml`.
4. Activate the environment, run `conda activate deetect`
5. Go to Deetect directory and run 'python main_window.py' 

## Usage

Deetect  has a graphical user interface (GUI) consisting of two windows. In the main window, the user selects the images to be analyzed and the methods to be applied. 
In the statistics window, by using the analysis file created by Deetect the selected test is applied and data is visualized in the selected graph type.

### Main Window
![Deetect_main_window](/images/deetect_main_window.png)

### Stats Window
![Deetect_stats_window](/images/deetect_stats_window.png)

## Input - Outputs

### Minimal Dataset including input and outputs

a minimal dataset with input and outputs is available at: [sample_2img_with_outputs.zip](https://edmond.mpdl.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.2OEMSK  )

### Input
* Deetect accepts files with tiff and tiff extensions.
* Allows multiple file selection
* If the folder is selected, all subfolders are scanned and all files with the appropriate extension are added to the queue for processing.

### Outputs
All the ouptuts are saved under a folder. This folder name contains the value of the following parameters: flow threshold, mask threshold, model, stack size and rotation
Under root result folder there are sub folders contains related analysis, therefore user can track result of each analysis steps easly.
* cp_orj_out : contains cellpose original outputs
* cp_png_out : contains cellpose resulting images (flows, overlay_mask, outlines) as .png
* double_out : contains dublication analysis results 
  + text files for 1) number of cells before and after double counting and 2) detailed information about intersection
  + images show 1) intersection and 2) removed cells
* e&s_out : contains Elimination and splitting analysis results 
  + text files for 1) number of cells  and 2) detailed information of cells for elimination process
  + image shows outlined cells after this process 
* png_stck* : contains the resulting images after stacking as .png

Also under the root folder, there is one text file contains the number of cells detected after each analysis. This file is used in stats window for statistics and visualization
  
  
--------------------
## publications
* The study is based on findings and data from a doctoral thesis by Felix Hoeren.
* This study was presented at the GCB 2021, Germany. You can find the submitted abstract [here](https://github.com/zgormez/Deetect/blob/main/papers/GCB_2021_G%C3%B6rmez_Hoeren_Richter_Krause_Troidl.pdf).
