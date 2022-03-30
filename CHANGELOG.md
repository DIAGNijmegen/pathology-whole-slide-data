# Changelog
---


### **Upcoming** (0.0.13)


### 0.0.12  (**Latest**)

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
 - version is read from verion.py
 - requirements are now read from the requirements file (contribution by Thijs Gelton)
 - url now points to github repo (contribution by Jakub Kaczmarzyk)
  

### 0.0.11)

**new features:**
 - image/annotations are now copied to separate folders
 - added source configuration 
 - added one-hot-encoding preset
 - dataset and labels are now sorted such that the generator will produce the same output when the seed is set
 - minor refactoring

**requirements:**
 - increased NumPy version to make it compatible with ASAP2.0


### 0.0.10
**bug fixes:**
 - fixed sampling bugs

### 0.0.9
**new features:**
 - increase speed sampling


### 0.0.8 
**bug fixes:**
 - fixed detection sampling bugs 

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
