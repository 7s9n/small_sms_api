from .grade import (
    GradeCreate,
    GradeInDB,
    GradeUpdate,
    GradesResponseModel,
    BasicGradeInfo,
)
from .subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectInDB,
    SubjectsResponseModel,
    BasicSubjectInfo,
)
from .grade_subject import (
    GradeSubjectOut,
    GradeSubjectsOut,
    GradeSubjectCreate,
    GradeSubjectUpdate,
    SubjectsGradeSchema,
    # SubjectGradeSchema,
    # SubjectsGradeAssignedSchema,
)
from .school_year import (
    SchoolYearInDB,
    SchoolYearCreate,
    SchoolYearUpdate,
    SchoolYearResponseModel,
)
from .student import (
    StudentCreate,
    StudentUpdate,
    StudentInDB,
    StudentPaginatedResponse,
    StudentRegistrations,
)
from .registration import (
    RegistrationCreate,
    RegistrationUpdate,
    RegistrationOut,
    RegistrationIn,
    RegistrationsResponseModel,
)
from .nationality import (
    NationalityCreate,
    NationalityUpdate,
    NationalityInDB,
    NationalitiesResponseModel,
)
from .levels import (
    LevelCreate,
    LevelUpdate,
    LevelInDB,
    LevelsResponseModel,
)
from .grading_scale import (
    GradingScaleCreate,
    GradingScaleUpdate,
    GradingScaleInDB,
    GradingScalesResponseModel,
)
from .user import (
    UserBase,
    UserInDB,
    UserInDBase,
    UserCreate,
    UserUpdate,
    AdminTeacherCreate,
    AdminTeacherUpdate,
    UserPaginatedResponse,
    AssignedTeacherCreateRequest,
    AssignedTeacherCreateInDB,
    AssignedTeacherInDB,
    UserChangePassword,
)
from .person import (
    PersonBase,
    PersonInDB,
    PersonInDBase,
    PersonCreate,
    PersonUpdate,
    AdminTeacherCreate,
    AdminTeacherUpdate,
)
from .token import (
    Token,
    TokenPayload,
)
from .mark import (
    MarkBase,
    MarkCreateInDB,
    MarkCreateRequest,
    MarkInDB,
    MarkUpdate,
    MonthEnum,
    SemasterEnum,
    MarksResponseModel,
    FinalMarkCreateRequest,
    FinalMarkCreateInDB,
    FinalMarkUpdate,
)