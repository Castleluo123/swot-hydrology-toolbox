# -*- coding: utf-8 -*-
"""
.. module:: lake_tile_filenames.py
    :synopsis: Deal with filenames used by LOCNES. There is one specific class per processor.

.. moduleauthor:: Claire POTTIER - CNES DSO/SI/TR

Copyright (c) 2018 CNES. All rights reserved.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

import cnes.common.lib.my_api as my_api
import cnes.common.lib_lake.locnes_variables as my_var
import cnes.common.serviceError as serviceError

   
def getInfoFromFilename(IN_filename, IN_type):
    """
    Retrieve orbit info from IN_filename
        
    :param IN_filename: input full path
    :type IN_filename: string
    :param IN_type: type of product =PIXC =PIXCVecRiver =LakeTile
    :type IN_type: string
        
    :return: dictionnary containing values found in IN_filename
    :rtype: dict
    """
    logger = logging.getLogger("locness_filename")
    # 0 - Init variables
    # 0.1 - Get pattern variables depending on IN_type
    if IN_type == "PIXC":
        if not os.path.basename(IN_filename).startswith(my_var.PIXC_PREFIX):
            logger.info("[getInfoFromFilename] Filename %s doesn't match with PIXC pattern %s" % (os.path.basename(IN_filename), my_var.PIXC_PATTERN_PRINT))
            return {}
        pattern = my_var.PIXC_PATTERN_IND
    elif IN_type == "PIXCVecRiver":
        if not os.path.basename(IN_filename).startswith(my_var.PIXCVEC_RIVER_PREFIX):
            logger.info("[getInfoFromFilename] Filename %s doesn't match with PIXCVecRiver pattern %s" % (os.path.basename(IN_filename), my_var.PIXCVEC_RIVER_PATTERN_PRINT))
            return {}
        pattern = my_var.PIXCVEC_RIVER_PATTERN_IND
    elif IN_type == "LakeTile":
        if not os.path.basename(IN_filename).startswith(my_var.LAKE_TILE_PREFIX):
            message = "[getInfoFromFilename] Filename %s doesn't match with LakeTile pattern %s" % (os.path.basename(IN_filename), my_var.LAKE_TILE_PATTERN_PRINT)
            raise serviceError.SASLakeTileError(message, logger)
#            my_api.exitWithError("[getInfoFromFilename] Filename %s doesn't match with LakeTile pattern %s" % (os.path.basename(IN_filename), my_var.LAKE_TILE_PATTERN_PRINT))
        pattern = my_var.LAKE_TILE_PATTERN_IND
    else:
        message = "Type %s unknown ; should be PIXC, PIXCVecRiver or LakeTile" % IN_type
        raise serviceError.SASLakeTileError(message, logger)
#        my_api.exitWithError("Type %s unknown ; should be PIXC, PIXCVecRiver or LakeTile")
    # 0.2 - Output dictionary
    OUT_dict = {}
        
    # 1 - Split basename
    basename_split = os.path.splitext(os.path.basename(IN_filename))[0].split("_")
    
    # 2 - Get values in filename
    # Add error check
    try:
        for key, val in pattern.items():  # Loop on keys
            TMP_val = None  # Init output value
            if val is not None:
                TMP_val = basename_split[val]  # Read value in filename if not None
            OUT_dict[key] = TMP_val  # Store value in output dictionary
    except:
        message = "[getInfoFromFilename] Filename %s doesn't match with LakeTile pattern %s" % (os.path.basename(IN_filename), my_var.LAKE_TILE_PATTERN_PRINT)
        raise serviceError.ProcessingError(message, logger)

    # 3 - Check if cycle and pass fields could be convert into int
    try:
       TMP_val = int(OUT_dict["cycle"])
       TMP_val = int(OUT_dict["pass"])
    except:
        message = "[getInfoFromFilename] Filename %s doesn't match with LakeTile pattern %s" % (os.path.basename(IN_filename), my_var.LAKE_TILE_PATTERN_PRINT)
        raise serviceError.ProcessingError(message, logger)
 
    return OUT_dict


#######################################


class lakeTileFilenames(object):

    def __init__(self, IN_pixc_file, IN_pixc_vec_river_file, IN_out_dir):
        """
        Constructor of LakeTile filenames
        
        :param IN_pixc_file: PIXC file full path
        :type IN_pixc_file: string
        :param IN_pixc_vec_river_file: PIXCVecRiver file full path
        :type IN_pixc_vec_river_file: string
        :param IN_out_dir: output directory
        :type IN_out_dir: string
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("[lakeTileFilenames] == INIT ==")
        
        # 1 - Init variables
        self.pixc_file = IN_pixc_file  # PIXC file full path
        self.pixc_vec_river_file = IN_pixc_vec_river_file  # PIXCVecRiver full path
        self.out_dir = IN_out_dir  # Output directory
        self.product_counter = 1  # Product counter
        
        # 2 - Retrieve info from PIXC filename
        TMP_dict = getInfoFromFilename(self.pixc_file, "PIXC")
        # 2.1 - Cycle number
        cycle_num = TMP_dict["cycle"]
        if cycle_num is None:
            self.cycle_num = 999
            logger.info("WARNING: cycle number has not been found in PIXC filename %s -> set to default value = %03d" % (os.path.basename(self.pixc_file), self.cycle_num))
        else:
            self.cycle_num = int(cycle_num)
            logger.info("Cycle number = %03d" % self.cycle_num)
        # 2.2 - Pass number
        pass_num = int(TMP_dict["pass"])  
        if pass_num is None:
            self.pass_num = 999
            logger.info("WARNING: pass number has not been found in PIXC filename %s -> set to default value = %03d" % (os.path.basename(self.pixc_file), self.pass_num))
        else:
            self.pass_num = int(pass_num)
            logger.info("Pass number = %03d" % self.pass_num)
        # 2.3 - Tile ref
        self.tile_ref = TMP_dict["tile_ref"]
        if self.tile_ref is None:
            self.tile_ref = "ttt-t"
            logger.info("WARNING: tile ref has not been found in PIXC filename %s -> set to default value = %s" % (os.path.basename(self.pixc_file), self.tile_ref))
        else:
            logger.info("Tile ref = %s" % self.tile_ref)
        # 2.4 - Start date
        self.start_date = TMP_dict["start_date"]
        if self.start_date is None:
            self.start_date = "yyyyMMddThhmmss"
            logger.info("WARNING: start date has not been found in PIXC filename %s -> set to default value = %s" % (os.path.basename(self.pixc_file), self.start_date))
        else:
            logger.info("Start date = %s" % self.start_date)
        # 2.5 - Stop date
        self.stop_date = TMP_dict["stop_date"]
        if self.stop_date is None:
            self.stop_date = "yyyyMMddThhmmss"
            logger.info("WARNING: stop date has not been found in PIXC filename %s -> set to default value = %s" % (os.path.basename(self.pixc_file), self.stop_date))
        else:
            logger.info("Stop date = %s" % self.stop_date)
        
        # 3 - Test compatibility of PIXCVecRiver filename with PIXC filename
        TMP_ok = self.testPixcVecRiverFilename()
        if TMP_ok:
            logger.info("PIXCVecRiver basename %s is compatible with PIXC basename %s" % (os.path.basename(self.pixc_vec_river_file), os.path.basename(self.pixc_file)))
        else:
            logger.info("WARNING: PIXCVecRiver basename %s IS NOT compatible with PIXC basename %s (cf. above)" % (os.path.basename(self.pixc_vec_river_file), os.path.basename(self.pixc_file)))
        
        # 4 - Compute output filenames
        self.computeLakeTileFilename_shp()  # LakeTile_shp filename
        self.computeLakeTileFilename_edge()  # LakeTile_edge filename
        self.computeLakeTileFilename_pixcvec()  # LakeTile_pixcvec filename
        
        # 5 - Compute Lake Id prefix
        self.computeLakeIdPrefix()
    
    #----------------------------------
    
    def computeLakeTileFilename_shp(self):
        """
        Compute LakeTile_shp full path
        """
        filename = my_var.LAKE_TILE_PATTERN % (self.cycle_num, self.pass_num, self.tile_ref, self.start_date, self.stop_date, my_var.LAKE_TILE_CRID, self.product_counter, my_var.LAKE_TILE_SHP_SUFFIX)
        self.lake_tile_shp_file = os.path.join(self.out_dir, filename)
        
        # Test existence and modify self.product_counter if needed
        while os.path.exists(self.lake_tile_shp_file):
            self.product_counter += 1
            filename = my_var.LAKE_TILE_PATTERN % (self.cycle_num, self.pass_num, self.tile_ref, self.start_date, self.stop_date, my_var.LAKE_TILE_CRID, self.product_counter, my_var.LAKE_TILE_SHP_SUFFIX)
            self.lake_tile_shp_file = os.path.join(self.out_dir, filename)
    
    def computeLakeTileFilename_edge(self):
        """
        Compute LakeTile_edge full path
        """
        filename = my_var.LAKE_TILE_PATTERN % (self.cycle_num, self.pass_num, self.tile_ref, self.start_date, self.stop_date, my_var.LAKE_TILE_CRID, self.product_counter, my_var.LAKE_TILE_EDGE_SUFFIX)
        self.lake_tile_edge_file = os.path.join(self.out_dir, filename)
        
        # Filename must not exist
        if os.path.exists(self.lake_tile_edge_file):
            message = "[locnes_filename] ERROR = %s already exists" % self.lake_tile_edge_file
            raise serviceError.SASLakeTileError(message, logger)
#            my_api.exitWithError("[locnes_filename] ERROR = %s already exists" % self.lake_tile_edge_file)
    
    def computeLakeTileFilename_pixcvec(self):
        """
        Compute LakeTile_pixcvec full path
        """
        filename = my_var.LAKE_TILE_PATTERN % (self.cycle_num, self.pass_num, self.tile_ref, self.start_date, self.stop_date, my_var.LAKE_TILE_CRID, self.product_counter, my_var.LAKE_TILE_PIXCVEC_SUFFIX)
        self.lake_tile_pixcvec_file = os.path.join(self.out_dir, filename)
        
        # Filename must not exist
        if os.path.exists(self.lake_tile_pixcvec_file)        :
            message = "[locnes_filename] ERROR = %s already exists" % self.lake_tile_pixcvec_file
            raise serviceError.SASLakeTileError(message, logger)
#            my_api.exitWithError("[locnes_filename] ERROR = %s already exists" % self.lake_tile_pixcvec_file)
    
    #----------------------------------
        
    def computeLakeIdPrefix(self):
        """
        Compute ID prefix for LakeTile product
        Id pattern is: 5_ccc_ppp_ttt-s_<increment_over_4_digits> where ccc is cycle number, ppp is pass number and ttt-s is tile ref with swath (ex: 45N-L for 45 North Left swath)
        """
        self.lake_id_prefix = "5_%03d_%03d_%s_" % (self.cycle_num, self.pass_num, self.tile_ref)
    
    #----------------------------------
    
    def testPixcVecRiverFilename(self):
        """
        Test if PIXCVecRiver filename is coherent with PIXC file, wrt (cycle, pass, tile) triplet
        
        :return: True is it's the case, or False if not
        :rtype: boolean
        """
        logger = logging.getLogger(self.__class__.__name__)
        # 0 - Init output boolean
        OUT_ok = True
        
        # 1 - Retrieve info from PIXCVecRiver filename
        TMP_dict = getInfoFromFilename(self.pixc_vec_river_file, "PIXCVecRiver")
        if len(TMP_dict) == 0:
            return False
        pixcvec_cycle_num = int(TMP_dict["cycle"])  # Cycle number
        pixcvec_pass_num = int(TMP_dict["pass"])  # Pass number
        pixcvec_tile_ref = TMP_dict["tile_ref"]  # Tile ref
        
        # 2 - Test each value
        # 2.1 - Cycle number
        if pixcvec_cycle_num != self.cycle_num:
            OUT_ok = False
            logger.info("WARNING: cycle number is not the same in PIXC (=%03d) and PIXCVecRiver (=%03d) filenames" % (self.cycle_num, pixcvec_cycle_num))
        # 2.2 - Pass number
        if pixcvec_pass_num != self.pass_num:
            OUT_ok = False
            logger.info("WARNING: pass number is not the same in PIXC (=%03d) and PIXCVecRiver (=%03d) filenames" % (self.pass_num, pixcvec_pass_num))
        # 2.3 - Tile ref
        if pixcvec_tile_ref != self.tile_ref:
            OUT_ok = False
            logger.info("WARNING: tile ref not the same in PIXC (=%s) and PIXCVecRiver (=%s) filenames" % (self.tile_ref, pixcvec_tile_ref))
        
        return OUT_ok


#######################################


class lakeSPFilenames(object):

    def __init__(self, IN_lake_tile_file_list, IN_continent, IN_out_dir):
        """
        Constructor of LakeSP filenames
        
        :param IN_lake_tile_file_list: list of LakeTile_shp files full path
        :type IN_lake_tile_file_list: list of string
        :param IN_continent: continent concerning the LakeSP
        :type IN_continent: string
        :param IN_out_dir: output directory
        :type IN_out_dir: string
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("[lakeSPFilenames] == INIT ==")
        
        # 1 - Init variables
        self.lake_tile_file_list = IN_lake_tile_file_list  # list of LakeTile_shp files full path
        self.out_dir = IN_out_dir  # Output directory
        self.product_counter = 1  # Product counter
        
        # 2 - Retrieve info from LakeTile filename
        TMP_dict = getInfoFromFilename(self.lake_tile_file_list[0], "LakeTile")
        # 2.1 - Cycle number
        cycle_num = TMP_dict["cycle"]
        if cycle_num is None:
            self.cycle_num = 999
            logger.info("WARNING: cycle number has not been found in LakeTile filename %s -> set to default value = %03d" % (os.path.basename(self.lake_tile_file), self.cycle_num))
        else:
            self.cycle_num = int(cycle_num)
            logger.info("Cycle number = %03d" % self.cycle_num)
        # 2.2 - Pass number
        pass_num = int(TMP_dict["pass"])  
        if pass_num is None:
            self.pass_num = 999
            logger.info("WARNING: pass number has not been found in LakeTile filename %s -> set to default value = %03d" % (os.path.basename(self.lake_tile_file), self.pass_num))
        else:
            self.pass_num = int(pass_num)
            logger.info("Pass number = %03d" % self.pass_num)
        # 2.3 - Continent
        if IN_continent is None:
            self.continent = "xx"
            my_api.printInfo("WARNING: continent is set to default value = %s" % self.continent)
        elif IN_continent == "WORLD":
            self.continent = None
            my_api.printInfo("WARNING: no continental split")
        else:
            self.continent = IN_continent
            logger.info("Continent = %s" % self.continent)
            
        # 3 - Retrieve start and stop dates from LakeTile_shp filenames
        self.computeStartStopDates()
        
        # 4 - Compute output filenames
        self.computeLakeSPFilename()  # LakeSP filename
        
        # 5 - Compute Lake Id prefix
        self.computeLakeIdPrefix()
    
    #----------------------------------
    
    def computeStartStopDates(self):
        """
        Compute start and stop dates from a list of LakeTile_shp filenames
        """
        
        # Init with 1st filename
        TMP_dict = getInfoFromFilename(self.lake_tile_file_list[0], "LakeTile")
        list_start = []
        list_start.append(TMP_dict["start_date"])
        list_stop = []
        list_stop.append(TMP_dict["stop_date"])
        
        # Process other files
        for curFile in self.lake_tile_file_list[1:]:
            TMP_dict = getInfoFromFilename(curFile, "LakeTile")
            list_start.append(TMP_dict["start_date"])
            list_stop.append(TMP_dict["stop_date"])
            
        # Sort dates
        list_start.sort()
        list_stop.sort()
        
        # Retrieve first and last dates
        self.start_date = list_start[0]
        self.stop_date = list_stop[-1]
    
    #----------------------------------
    
    def computeLakeSPFilename(self):
        """
        Compute LakeSP full path
        """
        
        if self.continent is None:
            filename = my_var.LAKE_SP_PATTERN_NO_CONT % (self.cycle_num, self.pass_num, self.start_date, self.stop_date, my_var.LAKE_SP_CRID, self.product_counter)
        else:
            filename = my_var.LAKE_SP_PATTERN % (self.cycle_num, self.pass_num, self.continent, self.start_date, self.stop_date, my_var.LAKE_SP_CRID, self.product_counter)
        self.lake_sp_file = os.path.join(self.out_dir, filename)
        
        # Test existence and modify self.product_counter if needed
        while os.path.exists(self.lake_sp_file):
            self.product_counter += 1
            if self.continent is None:
                filename = my_var.LAKE_SP_PATTERN_NO_CONT % (self.cycle_num, self.pass_num, self.start_date, self.stop_date, my_var.LAKE_SP_CRID, self.product_counter)
            else:
                filename = my_var.LAKE_SP_PATTERN % (self.cycle_num, self.pass_num, self.continent, self.start_date, self.stop_date, my_var.LAKE_SP_CRID, self.product_counter)
            self.lake_sp_file = os.path.join(self.out_dir, filename)
    
    #----------------------------------
        
    def computeLakeIdPrefix(self):
        """
        Compute ID prefix for LakeSP product
        Id pattern is: 5_ccc_ppp_CC_<increment_over_4_digits> where ccc is cycle number, ppp is pass number and CC is continent ref
        """
        if self.continent is None:
            self.lake_id_prefix = "5_%03d_%03d_" % (self.cycle_num, self.pass_num)
        else:
            self.lake_id_prefix = "5_%03d_%03d_%s_" % (self.cycle_num, self.pass_num, self.continent)


#######################################
        

def computePixcvecFilename(IN_laketile_pixcvec_filename, IN_output_dir):
    """
    Compute L2_HR_PIXCVec filename from L2_HR_LakeTile_pixcvec filename
    
    :param IN_laketile_pixcvec_filename: L2_HR_LakeTile_pixcvec filename to convert
    :type IN_laketile_filename: string
    :param IN_output_dir: output directory
    :type IN_output_dir: string
    """
    
    # Init variables
    product_counter = 1
    
    # Get infos from input LakeTile_pixcvec filename
    TMP_dict = getInfoFromFilename(IN_laketile_pixcvec_filename, "LakeTile")
    
    # Compute associated PIXCVec filename
    filename = my_var.PIXCVEC_PATTERN % (int(TMP_dict["cycle"]), int(TMP_dict["pass"]), TMP_dict["tile_ref"], TMP_dict["start_date"], TMP_dict["stop_date"], my_var.LAKE_SP_CRID, product_counter)
    OUT_filename = os.path.join(IN_output_dir, filename)
    
    while os.path.exists(OUT_filename):
        product_counter += 1
        filename = my_var.PIXCVEC_PATTERN % (int(TMP_dict["cycle"]), int(TMP_dict["pass"]), TMP_dict["tile_ref"], TMP_dict["start_date"], TMP_dict["stop_date"], my_var.LAKE_SP_CRID, product_counter)
        OUT_filename = os.path.join(IN_output_dir, filename)
    
    return OUT_filename
    
