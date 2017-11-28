#!usr/bin/python

import re
from os import listdir, getcwd
import sys
from os.path import isfile, join

def extractFiles():
    '''extracting files from the directory.
       if the command line argument is provided, then use that
       else, use the current directory.
    '''
    if len(sys.argv) > 1:
        # check if the filename actually exists
        try:
            mypath = str(sys.argv[1])                     
            files = [fil for fil in listdir(mypath) if isfile(join(mypath, fil))]
            # checking if the files list is empty
            if not files:
                print("No files in the directory.")
            else:
                createExtensions(files)
        except OSError as e:
            print("Invalid path!")            
    else:
        mypath = getcwd()    
        # extracting the item into a list if the item is a file
        files = [fil for fil in listdir(mypath) if isfile(join(mypath, fil))]    
        # checking if the files list is empty
        if not files:
            print("No files in the directory.")
        else:
            createExtensions(files)

def createExtensions(files):
    ''' Extracting extentions from file names and segregating files based on the extentions.
        parameter: 
            file: files in the directory
    '''    
    ext = []
    
    # file extension will be everthing after the last period in the string
    for i in files:
        # traversing the string from the end
        j=len(i)-1
        name = ""
        while(j>0):
            # break once period is found
            if(i[j]=="."):
                # adding period to create the proper extension
                name = i[j]+name
                break
            else:
                # concatinating string characters to create the extension
                name = i[j]+name
                j = j-1
        ext.append(name)
    
    # creating an empty dictonary of lists with keys as extensions
    file_extensions = {
        i: []
        for i in set(ext)
    }
    
    # populating the dictonary based on the extension of the file
    for i in range(len(ext)):
        file_extensions[ext[i]].append(files[i])

    for extension in file_extensions:
        extractNum(file_extensions, extension)

def extractNum(file_extensions, extension):
    '''Extracting all the numbers from the filenames.
       parameters:
           file_extension: dictonary with filenames arranged based on file extension as keys
           keys: file extensions
    '''
    result_list = []
    name_list = []
        
    for files in file_extensions[extension]:
        num_list=[]
        name = ""
        start = 0        
        # iterating over all the digits present in the file name
        for num in re.finditer(r"\d+",files):
            num_len = num.end() - num.start()
            # creating a list of the digit, length of the digit, starting index, ending index
            num_list.append([num.group(0), num_len, num.start(), num.end()])            
            # creating file names with "*" in places of digits. eg: file01_0040.rgb will be file**_****.rgb
            # this way we will be able to keep track of file following same name and similar numbering format
            last = num.start()
            name = name + files[start:last] + "*"*num_len 
            start = num.end()        
        # adding file extension
        name = name + files[start:]
        # creating a list with "*" replaced filenames
        # for files with no digits, append the original file name else add the replaced version
        if name == "":
            name_list.append(files)
        else:
            name_list.append(name)            
        # adding the list of extracted number to a new list to keep track of numbers from different files
        result_list.append(num_list)
    
    checkMatch(result_list, name_list, file_extensions, extension)

def checkMatch(result_list, name_list, file_extensions, keys):
    '''Checkning if the filenames names match.
    '''
    result_dict = {}
    # a list to keep track of the matching files.
    # populating the list initially with 0s and changing to 1 the moment a match is found
    tracking = [0] * len(result_list)

    # comparing the elements in the result_list in pairs of two. 
    for i in range(len(result_list)-1):
        isEqual = False
        curr = result_list[i]
        after = result_list[i+1]        
        '''compare for similarity only if the lists are non empty, the name pattern is similar
           and the number of digits in the file names are similar.
           
           For the filenames containing digits and neither similar to the filename before
           or the filename after, their tracking will remain 0 indicating that
           such files will be added as it is since they are unique.
        '''
        if((len(curr)>0 and len(after)>0) and (len(curr)==len(after)) and (name_list[i] == name_list[i+1])):
            for j in range(len(curr)):                
                # subtracting each part of the list.
                # for similar files all the infomation will subtract to 0 except the integer sequence 
                check = [int(a)-int(b) for a,b in zip(after[j],curr[j])]
                # if the check is 0 that would mean that the digits in the filename
                # and the location on the digits is matching which would mean the basic filename is same
                if ((len(curr)>1) and set(check)=={0}):
                    isEqual = True
                    # performing the C style printing
                    filename = fileName(curr[j][2], curr[j][0], curr[j][3], name_list[i])
                    # if the filename is not already present in the dictonary, create a key with the value as empty list
                    if(filename not in result_dict):
                        result_dict[filename] = []
                # if there is only one number present in the filenames, replacing the number with correspoinding zero padding
                elif (len(curr)==1):
                    isEqual = True
                    # replacing the number with the corresponding zero padding
                    filename = zero_padding(name_list[i].count("*"), name_list[i])
                    if(filename not in result_dict):
                        result_dict[filename] = []
                    start = int(curr[j][0])
                    end = int(after[j][0])
                else:
                    # if the filenames is already present, add the extracted number to form the number sequence
                    start = int(curr[j][0])
                    end = int(after[j][0])
                    
            # if for a pair isEqual is True, then the tracking for both is set to 1
            if(isEqual):
                tracking[i] = 1
                tracking[i+1] = 1
                result_dict[filename].append(start)
                result_dict[filename].append(end)
           
    checkTracking(file_extensions, keys, tracking, result_dict)

def checkTracking(file_extensions, keys, tracking, result_dict):
    '''adding the original file names of the files with tracking 0
    '''
    for k in range(len(tracking)):
        if tracking[k] == 0:
            result_dict[file_extensions[keys][k]] = file_extensions[keys][k]
            
    compactNumform(result_dict)

def fileName(num_start, num, num_end, name_list):
    ''' performing the c style printing. eg: file01_0040.rgb as file01_%04d.rgb
        parameters:
            num_start: starting index of the digits
            num: the digit sequence
            num_end: ending index of the digits
            name_list: filenames with digits replaced with "*"
    '''
    length = num_end - num_start    
    # for the digits which are part of the common file name and not the part of integer sequence
    # replace the "*" with the original digit(s)
    filename = name_list[:num_start] + name_list[num_start:num_end].replace("*"*length,num) + name_list[num_end:]
    # counting how many "*" are remaining after replacing the digits which are part of filename
    return zero_padding(filename.count("*"), filename)

def zero_padding(frequency, filename):
    '''calculating the zero padding required to create C style format
       parameters:
           frequence: number of digits in the number
           filename: name of the file on which operation is being performed
    '''
    if frequency > 2:
        filename = filename.replace("*"*frequency, "%0"+str(frequency)+"d")
    else:
        filename = filename.replace("*"*frequency, "%d")    
    return filename

def compactNumform(result_dict):
    '''converting integer sequence into a compact form. eg: [1,2,3,4] = 1-4
    '''
    count = {}
    
    for key in result_dict:        
        # for the unique files, the key and value will be the same.
        # and for others the value will be the list with integer sequence
        if key != result_dict[key]:            
            # taking all the unique numbers from the list
            result_dict[key] = list(set(result_dict[key]))
            ranges = []            
            # checking if the current and next number are consecutive
            # and appending them if they are not
            for t in zip(result_dict[key], result_dict[key][1:]):
                if (t[0]+1 != t[1]):
                    ranges.append(t[0])
                    ranges.append(t[1])
            iranges = iter(result_dict[key][0:1] + ranges + result_dict[key][-1:])
            count[key] = len(set(result_dict[key]))
            result_dict[key] = (', '.join([str(n) + '-' + str(next(iranges)) for n in iranges]))
        else:
            count[key] = 1
    #print(result_dict)
    finalPrint(result_dict, count)

def finalPrint(result_dict, count):
    ''' printing in the required format with file count, c style format, compact form of integer sequence
        parameters:
            result_dict: dictonary with file numbers extracted based on c style filename pattern as the key
            count: number of files of a partcular name pattern
    '''
    for key in result_dict:
        if count[key] > 1:
            print(str(count[key]) + " " + key + "       " + result_dict[key])
        else:
            print(str(count[key]) + " " + key)

def main():
    extractFiles()

if __name__ == "__main__":
   
   main()
