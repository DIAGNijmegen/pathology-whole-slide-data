# Changelog
---
#### **Upcoming** (0.0.16)  


### (0.0.15) (**Latest**)

**bug fixes:**
- install of 0.0.14 failed due to not ruamel import error. 


### (0.0.14)

**new features:**
- updated to ASAP2.1
- cucim image backend
- tiffslide image backend  (Contributed by Rishi Jumani)
- s3 asap parser  (Contributed by Rishi Jumani)
- switched to rtree 
- updated patch iterator
- get shape_from_spacing method in wsi
- loading slides < 2.0 spacing gives warning
- added check coordinates for point
- method for annotations and sampling annotations per label
- grand-challenge annotations to asap format
- mask patch with annotations
- load empty files gives warning
- added writer factory functions


**breaking changes**
- removed redundant shift coordinates method

**docs:**
- included binder files

**requirements:**
 - added
  - jsonschema>=4.4.0
  - matplotlib>=3.3.1
  - rtree>=1.0.0

**bug fixes:**
- count for specific sample labels
- hed callback  
- wsi file reference
- virtum parser
- areaannotationsampler
- plotting: fixed plot batch function
- plotting: scaling in base coordinates in plot annotations (Contributed by Robin Lomans)


### (0.0.13) (**Latest**)

**refactoring**
- renamed orginal_path to original_path in File

**new features:**
- added patch iterator

**bug fixes:**
- install of 0.0.12 failed due to not finding requirements.txt. Requirements are now again specified in the setup.py. 

---

### 0.0.12 

**breaking changes**
 - specific code for external software has been moved to accessories
-  label weights in WeightedLabelSampler are now specified via a dictionary

**refactoring**
 - parsing of annotation files has been refactored and now includes a JSON schema
 - enhance shape and spacing error messages (Contributed by Jakub Kaczmarzyk)
  
**new features:**
 - accessories are loaded with package import
 - WholeSlideAnnotationParser based on JSON schema
 - JSON schema can be used to serialize annotations
 - albumentations callback (contributation by Thijs Gelton)
 - HedCallback augmentation
 - 'none' labels are sorted below other labels
 - associater classes StemSplitterAssociater and AnyOneAssociater
 - exact match option for associate_files
 - clip polygon and check for valid boxed in detection patch label sampler
 - MaskPatchLabelSampler now accepts a spacing
 - auxiliary method to create yaml from folders with data (contributation by Thijs Gelton)
 
**bug fixes:**
 - fix for randomness in uniform point sampler 

**setup file**
 - version is read from version.py
 - requirements are now read from the requirements file (contribution by Thijs Gelton)
 - url now points to github repo (contribution by Jakub Kaczmarzyk)
  
---

### 0.0.11

**new features:**
 - image/annotations are now copied to separate folders
 - added source configuration 
 - added one-hot-encoding preset
 - dataset and labels are now sorted such that the generator will produce the same output when the seed is set
 - minor refactoring

**requirements:**
 - increased NumPy version to make it compatible with ASAP2.0

---

### 0.0.10
**bug fixes:**
 - fixed sampling bugs

---

### 0.0.9
**new features:**
 - increase speed sampling

---

### 0.0.8 
**bug fixes:**
 - fixed detection sampling bugs 

---

### 0.0.7
**new features:**
 - detection support
 - pyvips image backend support
 - multiple spacings support
 - update call from producers to commander

 - fixed: copy data failed on first trial when using multiple cpus

---
### 0.0.6 
 - No change log or this version
---
### 0.0.5

- No change log or this version
---
### 0.0.4
- No change log or this version
---
### 0.0.3
- No change log or this version
---
### 0.0.2
- No change log or this version
---
### 0.0.1
- No change log or this version
---

<!-- 
**new features:**

**bug fixes:**

**depreciations:** -->
