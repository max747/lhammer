{-
CopyRight (C) 2008 Chen Zheng <nkchenz@gmail.com> 
Distributed under terms of GPL v2

P-99: Ninety-Nine Prolog Problems
https://prof.ti.bfh.ch/hew1/informatik3/prolog/p-99/
         
part of haskell solutions
http://www.haskell.org/haskellwiki/H-99:_Ninety-Nine_Haskell_Problems
-}

-- 模块导入必须放在前面
import Data.List (group)

-- dict, 异构list for haskell
-- tree bst rbtree
-- 定义一个容器类型，可以包含其他所有类型
--     Containor
-- 用户自己知道要存的数据类型是什么，自省机制，运行时根据类型选取合适的函数

-- P01. 获得列表的最后一个元素
-- 内置last函数
my_last xs = head $ reverse xs
-- > my_last [1, 2, 3]
-- 3

-- P02. 获得倒数第二个元素
-- init是获得列表除最后元素之外的所有元素，对其再取last即可
-- 空列表情况没有考虑
second_last xs = last $ init xs
second_last2 xs = head $ tail $ reverse xs
-- > second_last [1, 2, 3]
-- 2
-- > second_last2 [1, 2, 3]
-- 2

-- P03. 获得第k个元素
-- 使用内置操作符 !!，第一个元素索引为0，需要将k减一
element_at xs k = xs !! (k - 1)
-- > element_at ['a', 'b', 'c', 'd', 'e'] 3
-- 'c'

-- P04. 获得列表长度
-- 内置length
my_length_ [] k = k
-- 使用尾递归
my_length_ (x:xs) k = my_length_ xs (k + 1)
my_length xs = my_length_ xs 0
-- > my_length []
-- 0
-- > my_length [1]
-- 1
-- > my_length [1, 2, 3]
-- 3


-- P05. 翻转列表
-- 内置reverse
my_reverse [] = []
my_reverse (x:xs) = (my_reverse xs) ++ [x] 
-- > my_reverse []
-- []
-- > my_reverse [1, 2, 3]
-- [3,2,1]

-- P06. 判断列表是否为回文
is_palindrome xs = xs == (reverse xs)
{-
> is_palindrome []
True
> is_palindrome [1, 2, 3]
False
> is_palindrome "abccba"
True
> is_palindrome [1, 2, 1]
True
-}

-- P07. 将嵌套列表扁平化
{-
列表元素必须是类型相同，嵌套列表[1, [2, 3], 4]在haskell中是不合法的，需要定义
新的数据结构，这里定义了一个通用的list类型: GenericList，与树有些类似。

- concatMap 对列表进行map并收集结果，其定义为
-- concatMap               :: (a -> [b]) -> [a] -> [b]
-- concatMap f  =  foldr ((++) . f) []
-- 可知f对列表元素的操作结果仍必须为一列表, f :: a -> [b]
-}
-- Elem, List是新类型GenericList的构造标识
data GenericList a = Elem a | List [GenericList a] 
my_flatten (Elem x) = [x]
my_flatten (List x) = concatMap my_flatten x
-- > list = List [Elem 1, List [Elem 2, List [Elem 3, Elem 4]], Elem 5]
-- > my_flatten list
-- [1,2,3,4,5]


-- P08. 去除连续的重复元素
-- 使用Data.List模块中的group函数，将相同邻近元素分组
compress xs = map head $ group xs
-- > compress ['a','a','a','a','b','c','c','a','a','d','e','e','e','e']
-- "abcade"
-- > compress [1, 1, 2, 1, 1, 3, 2, 2]
-- [1,2,1,3,2]


-- P09. 将连续重复的元素放在子列表中
-- takeWhile, dropWhile 根据条件截取列表
-- > span (< 3) [1,2,3,4,1,2,3,4]
-- ([1,2],[3,4,1,2,3,4])
-- > span (< 9) [1,2,3]
-- ([1,2,3],[])
pack xs = group xs
-- > pack []
-- []
-- > pack ['a','a','a','a','b','c','c','a','a','d','e','e','e','e']
-- ["aaaa","b","cc","aa","d","eeee"]
-- > pack [1, 1, 2, 1, 1, 3, 2, 2]
-- [[1,1],[2],[1,1],[3],[2,2]]


-- P10. 对问题9返回的列表进行编码，每个子列表用(length, elem)代替
encode xs = map f $ group xs
    where f x = (length x, head x)
{-
基本思路就是对列表进行遍历，其他解法:
lambda表达式 map (\x -> (length x,head x)) (group xs)
列表构造 [(length x, head x) | x <- group xs]
tuple构造符'&&&'  map (length &&& head) $ group xs

> encode []
[]
> encode ['a']
[(1,'a')]
> encode ['a','a','a','a','b','c','c','a','a','d','e','e','e','e']
[(4,'a'),(1,'b'),(2,'c'),(2,'a'),(1,'d'),(4,'e')]
> encode [1, 1, 2, 1, 1, 3, 2, 2]
[(2,1),(1,2),(2,1),(1,3),(2,2)]
-}

-- P11.
