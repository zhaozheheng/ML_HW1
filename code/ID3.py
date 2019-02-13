import math
import time

global prunNum
prunNum = 30


def loadDataSet(filename):
    fr = open(filename)
    dataSet = []
    for line in fr.readlines():
        lineStr = line.split(',')
        lineStr[-1] = lineStr[-1].replace('\n', '')
        if len(lineStr[0]) == 1:
            dataSet.append(lineStr)
        else:
            attrName = lineStr
    return dataSet, attrName


def calcEntropy(pNum, nNum):
    if pNum == 0 or nNum == 0:
        return 0.0
    else:
        pPro = pNum / (pNum + nNum)
        nPro = nNum / (pNum + nNum)
        return -(pPro * math.log(pPro, 2) + nPro * math.log(nPro, 2))


def selectBest(dataSet):
    rNum = len(dataSet)
    cNum = len(dataSet[0])
    entropy = 0.0
    pNum = 0.0
    nNum = 0.0
    for i in range(rNum):
        if dataSet[i][-1] == '1':
            pNum = pNum + 1.0
        else:
            nNum = nNum + 1.0
    entropy = calcEntropy(pNum, nNum)

    infoGain = 0.0
    bestAttr = -1
    for i in range(cNum - 1):
        ppNum = 0.0
        pnNum = 0.0
        npNum = 0.0
        nnNum = 0.0
        for j in range(rNum):
            if dataSet[j][i] == '1':
                if dataSet[j][-1] == '1':
                    ppNum = ppNum + 1.0
                else:
                    pnNum = pnNum + 1.0
            else:
                if dataSet[j][-1] == '1':
                    npNum = npNum + 1.0
                else:
                    nnNum = nnNum + 1.0
        pEntro = calcEntropy(ppNum, pnNum)
        nEntro = calcEntropy(npNum, nnNum)
        condEntro = pEntro * (ppNum + pnNum) / float(rNum) + \
                    nEntro * (npNum + nnNum) / float(rNum)
        infoGainTmp = entropy - condEntro
        if infoGainTmp >= infoGain:
            infoGain = infoGainTmp
            bestAttr = i

    return bestAttr


def divDataSet(dataSet, bestAttr):
    rNum = len(dataSet)
    cNum = len(dataSet[0])
    ppNum = 0
    pnNum = 0
    npNum = 0
    nnNum = 0
    for line in dataSet:
        if line[bestAttr] == '1':
            if line[-1] == '1':
                ppNum = ppNum + 1
            else:
                pnNum = pnNum + 1
        else:
            if line[-1] == '1':
                npNum = npNum + 1
            else:
                nnNum = nnNum + 1
    if ppNum >= pnNum:
        mjr1 = 1
    else:
        mjr1 = 0
    if npNum >= nnNum:
        mjr0 = 1
    else:
        mjr0 = 0

    pDataSet = []
    nDataSet = []
    for line in dataSet:
        tmp = line[bestAttr]
        newLine = [line[i] for i in range(cNum) if i != bestAttr]
        if tmp == '1':
            pDataSet.append(newLine)
        else:
            nDataSet.append(newLine)

    return pDataSet, nDataSet, mjr1, mjr0


def isLeave(dataSet):
    if len(dataSet) == 0:
        return True
    if len(dataSet[0]) == 1:
        return True
    flag = dataSet[0][-1]
    for entry in dataSet:
        if entry[-1] != flag:
            return False
    return True


def createNode(dataSet, node, mjr):
    if isLeave(dataSet) == True:
        if mjr == 1:
            node.append(1)
            return
        else:
            node.append(0)
            return
    else:
        bestAttr = selectBest(dataSet)
        pDataSet, nDataSet, mjr1, mjr0 = divDataSet(dataSet, bestAttr)
        node.append(bestAttr)
        node.append([])
        node.append([])
        createNode(pDataSet, node[1], mjr1)
        createNode(nDataSet, node[2], mjr0)
        return


def createTree(filename):
    dataSet, attrName = loadDataSet(filename)
    tree = []
    if dataSet[0][-1] == '1':
        initMjr = 1
    else:
        initMjr = 0
    createNode(dataSet, tree, initMjr)
    return tree, attrName


def printTree(tree, depth, lastIndex, flag, attrName):
    if len(tree) == 0:
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    if len(tree) == 1:
        if depth == 0:
            print str(tree[0])
        else:
            for i in range(depth - 1):
                print "| ",
            print attrName[lastIndex] + " = " + str(flag) + " : " + str(tree[0])
        return
    else:
        if depth != 0:
            for i in range(depth - 1):
                print "| ",
            print attrName[lastIndex] + " = " + str(flag) + " : "
            newAttrName = [attrName[i] for i in range(len(attrName)) if i != lastIndex]
        else:
            newAttrName = attrName
        printTree(tree[1], depth + 1, tree[0], 1, newAttrName)
        printTree(tree[2], depth + 1, tree[0], 0, newAttrName)
        return


def testSingle(attr, tree):
    if len(tree) == 1:
        return tree[0]
    else:
        tmp = attr[tree[0]]
        newAttr = [attr[i] for i in range(len(attr)) if i != tree[0]]
        if tmp == '1':
            return testSingle(newAttr, tree[1])
        else:
            return testSingle(newAttr, tree[2])


def test(tree, dataSet, attrName):
    totalNum = len(dataSet)
    correctNum = 0
    for attribute in dataSet:
        flag = int(attribute[-1])
        if testSingle(attribute, tree) == flag:
            correctNum = correctNum + 1
    return float(correctNum) / float(totalNum)


def calcLeaves(tree):
    if len(tree) == 1:
        return 1
    else:
        return calcLeaves(tree[1]) + calcLeaves(tree[2])


def totalNodes(tree):
    if len(tree) == 1:
        return 1
    else:
        return totalNodes(tree[1]) + totalNodes(tree[2]) + 1


def getMjr(dataSet):
    pNum = 0
    nNum = 0
    for entry in dataSet:
        if entry[-1] == '1':
            pNum = pNum + 1
        else:
            nNum = nNum + 1

    if pNum >= nNum:
        mjr = 1
    else:
        mjr = 0

    pRate = float(pNum) / float(pNum + nNum)
    if pRate >= 0.5:
        corRate = pRate
    else:
        corRate = 1 - pRate
    return mjr, corRate


def cut(tree, dataSet):
    if len(tree) == 1:
        return
    tree.pop()
    tree.pop()
    tree[0], useless = getMjr(dataSet)
    return


def pruning(tree, dataSet, attrName):
    if len(tree) == 1:
        return
    if len(dataSet) == 0:
        return
    if len(dataSet[0]) == 1:
        return

    global prunNum
    pDataSet, nDataSet, u1, u2 = divDataSet(dataSet, tree[0])
    pruning(tree[1], pDataSet, attrName)
    pruning(tree[2], nDataSet, attrName)
    mjr, corRateSin = getMjr(dataSet)
    corRate = test(tree, dataSet, attrName)
    if corRateSin > corRate and prunNum > 0:
        cut(tree, dataSet)
        prunNum = prunNum - 1
    return


def main():
    trainingfilePath = raw_input("Enter the training file path: \n")
    validationfilePath = raw_input("Enter the validation file path: \n")
    testfilePath = raw_input("Enter the test file path: \n")
    prunFac = float(raw_input("Enter the pruning factor: \n"))
    tree, attrName = createTree(trainingfilePath)
    printTree(tree, 0, 0, 0, attrName)
    trainingSet, attrName = loadDataSet(trainingfilePath)
    validSet, attrName = loadDataSet(validationfilePath)
    testSet, attrName = loadDataSet(testfilePath)
    print "Pre-Pruned Accuracy"
    print "------------------------------------- "
    print "Number of training instances = " + str(len(trainingSet))
    print "Number of training attributes = " + str(len(trainingSet[0]) - 1)
    print "Total number of nodes in the tree = " + str(totalNodes(tree))
    print "Number of leaf nodes in the tree = " + str(calcLeaves(tree))
    print "Accuracy of the model on the training dataset = " + str(test(tree, trainingSet, attrName))
    print ""
    print "Number of validation instances = " + str(len(validSet))
    print "Number of validation attributes = " + str(len(validSet[0]) - 1)
    print "Accuracy of the model on the validation dataset before pruning = " + str(test(tree, validSet, attrName))
    print ""
    print "Number of testing instances = " + str(len(testSet))
    print "Number of testing attributes = " + str(len(trainingSet[0]) - 1)
    print "Accuracy of the model on the testing dataset = " + str(test(tree, testSet, attrName))
    #prunFac = 0.2
    global prunNum
    prunNum = prunFac * totalNodes(tree)
    pruning(tree, validSet, attrName)
    printTree(tree, 0, 0, 0, attrName)
    print "Post-Pruned Accuracy \n-------------------------------------"
    print "Number of training instances = " + str(len(trainingSet))
    print "Number of training attributes = " + str(len(trainingSet[0]) - 1)
    print "Total number of nodes in the tree = " + str(totalNodes(tree))
    print "Number of leaf nodes in the tree = " + str(calcLeaves(tree))
    print "Accuracy of the model on the training dataset = " + str(test(tree, trainingSet, attrName))
    print ""
    print "Number of validation instances = " + str(len(validSet))
    print "Number of validation attributes = " + str(len(validSet[0]) - 1)
    print "Accuracy of the model on the validation dataset after pruning = " + str(test(tree, validSet, attrName))
    print ""
    print "Number of testing instances = " + str(len(testSet))
    print "Number of testing attributes = " + str(len(trainingSet[0]) - 1)
    print "Accuracy of the model on the testing dataset = " + str(test(tree, testSet, attrName))


main()
