# 33-2nd-BranchTime-backend
김민정, 임한구

# 33기 2차 프로젝트 BranchTime팀

<img width="544" alt="로고" src="https://user-images.githubusercontent.com/103249222/174513495-04076b0d-316c-4570-9df1-f7ea24589382.png">


<br/>

## 🌼 프로젝트 소개 🌼


* 글쓰기에 최적화 된 블로그 플랫폼 사이트를 선정했습니다.
* 짧은 기간동안 개발에 집중할 수 있도록 디자인과 기획 일부를 [브런치](https://brunch.co.kr)를 참조하여 학습목적으로 만들었습니다.
* 실무 수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
* 이 프로젝트에서 사용하고 있는 로고와 배너는 해당 프로젝트 팀원 소유이므로 해당 프로젝트 외부인이 사용할 수 없습니다.

![ezgif-2-79bca24642](https://user-images.githubusercontent.com/103249222/178927358-2720b3b3-0b7c-4e07-9079-9c0492471147.gif)
![ezgif-2-1b836a84a8](https://user-images.githubusercontent.com/103249222/178927333-25df49a0-41e4-49d6-8290-d9d8031d38da.gif)
![ezgif-2-3243a49863](https://user-images.githubusercontent.com/103249222/178927359-e9799464-697d-425e-920b-dca8c7c2698d.gif)
![ezgif-2-d2c95f9493](https://user-images.githubusercontent.com/103249222/178927362-48e20ef9-918d-4ce9-a1c3-3f198694da1d.gif)
![ezgif-2-1f456bae0a](https://user-images.githubusercontent.com/103249222/178927345-70473484-0ffb-4856-9d89-ea3bb4186529.gif)
![ezgif-2-3fb3c5702c](https://user-images.githubusercontent.com/103249222/178927355-5c85e849-5b3d-496a-98a4-e5a6e34d856b.gif)


<br/>

## 🌼 개발 인원 및 기간 🌼
**개발기간** : 2022/06/07~2022/06/17

<br/>

**개발인원 및 파트** : 
#### Frontend
- 박슬기 🐷 : Nav, 글 쓰기 페이지
- 김형겸 🍋 : 메인 페이지, 검색, 로그인
- 박주영 🌟 : 글 목록 페이지, 글 상세 페이지, 
- 신윤지 🐜 : 마이 페이지, 북 애니메이션

#### Backend
- 임한구 🎅🏻 : 소셜로그인, 마이페이지, 카테고리 리스트, 포스팅 리스트, 포스팅 디테일
- 김민정 🌟 : 포스팅 작성, 댓글 작성 및 리스트, 이메일 제안하기, 작가 리스트 

<br/>

## 🌼 기술 🌼
**Front-End** : React.js 
<br/>
**Back-End** : Python, Django web framework, MySQL, pyjwt, AWS
<br/>
**Common** : Git-Hub, slack, trello

<br/>

## 🌼 페이지별 구현 사항 🌼

### Users APP
#### 1. KakaoLoginView
 - 카카오 소셜로그인 API를 활용한 로그인 기능
 - 프론트엔드에서 인증후 code반환하면 그 code를 활용하여 access_token을 받아 사용자 정보(email, name, thumbnail)받아 Database에 저장.
 - 사용자 정보를 DB에 저장시 socialaccount DB에 api에서 제공하는 PK값과 해당하는 회사명("kakao")를 동시에 저장 (transantion활용)
#### 2. UserDetailView
 - 로그인하여 마이페이지 접속시 GET요청에 의해 반환
 - 로그인 데코레이터 활용하여 사용자 DB접근하여 사용자 정보 반환
#### 3. ProfileUpdate 
 - 마이페이지 수정  
 - AWS(S3) 활용 프로필사진 변경
 - 사용자 이름, 사용자 소개 수정

### contents APP
#### 1. CategoryView
 - 메인화면 및 post list화면에 필요한 카테고리 조회 기능

#### 2. PostListView
 - 작성된 글들의 리스트들을 메인카테고리별 또는 서브카테고리별 조회하는 기능

#### 3. PostImageUpload
 - 글작성시 글 본문에 이미지 삽입을 하기 위한 기능으로 이미지가 저장된 URL을 반환

#### 4. PostUploadView
 - 글 작성을 위한 기능으로 글제목, 글소제목, 썸네일이미지 또는 썸네일부분 배경색상, 본문내용, 리닝시간, 서브카테고리를 받아 저장하는 기능
 - 섬네일 이미지는 별도로 S3를 통해 저장되어 URL을 DB에 저장하는 기능

#### 5. PostDetailView
 - PostUploadView로 작성된 글을 상세하게 보는 페이지로 댓글이 있다면 댓글도 같이 반환
 - 글뿐만아니라 작가정보와 좋아요 및 구독수도 함께 반환

#### 6. CommentUploadView
 - 글에 해당하는 댓글을 업로드 하는 기능
 - 댓글에 이미지를 함께 포함할 수 있으며 이미지는 S3에 저장되고 DB에는 URL을 저장

### 7. CommentUpdateView
 - 댓글 수정 및 삭제 기능
 - 업로드는 post메소드 업데이트는 patch를 사용하려하였으나 patch메소드에서는 S3가 동작하지않아 별도의 update클래스를 만들어 기능 구현
 - 댓글 업데이트는 post메소드로 구현, 댓글 삭제는 delete메소드로 구현


### authors APP
#### 1. ProposalView
 - 작가에게 제안하기 메일 발송 기능
 - utils의 goolge_email_api를 활용해 generate_token 함수를 이용하여 토큰 발급 후 send_mail 함수를 이용해 메일 보내기 수행

#### 2. AuthorListView
 - 메인페이지의 추천작가를 위해 서브카테고리에 따라 작가를 반환해주는 기능 구현

#### 3. AuthorDetailView
 - AuthorListView에서 반환해주는 작가리스트 정보의 상세정보를 반환해주는 기능

### core APP
 - models.py 에 TimeStamp 기능을 담당하기위해 구현

### utils directory
 - 모든 APP에서 중복되어 사용되는 기능들을 모아둔 directory
 
#### 1. login_decorator
 - login시 발급되는 access_token을 통해 디코딩하여 DB와 비교하여 인가 유무를 판단해주는 기능 담당
#### 2. google_email_api
 - 발송인가를 위한 token발급과 메일발송을 담당
#### 3. fileuploader_api
 - AWS S3에 파일을 저장, 삭제 하는 기능담당


<br/>

## 🌼 프로젝트 진행 과정 🌼
||Trello|Daily Standup Meeting|
|------|---|---|
|협업 방식|칸반보드를 활용한 회의록 작성 및 진행상황 공유|매일 아침 30분동안 진행사항과 오늘 할 작업 내용 공유|
|IMG|<img width="1408" alt="트렐로" src="https://user-images.githubusercontent.com/103249222/174526348-44380889-6b7d-407a-90af-98c7c0480b00.png">|![트렐로디테일](https://user-images.githubusercontent.com/103249222/174526409-d2501faa-6ad2-49ca-9966-af12a7d66e65.png)|





